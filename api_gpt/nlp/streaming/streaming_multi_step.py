from typing import Optional
from numpy import False_
import openai
import requests
import json
from api_gpt.integrations.app_info import AppInfoHandler
import sseclient
from timeit import default_timer as timer
from threading import Thread

from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.nlp.exploration import (
    api_call_json_to_intent,
    fix_extracted_str,
    generate_intent_type_from_name,
)

from api_gpt.nlp.exploration_simple import (
    SINGLE_EXPLOR_SYSTEM_PROMPT,
    parse_json_from_string,
    parse_workflow_data_from_json,
)
from google.protobuf.json_format import MessageToJson
from api_gpt.nlp.streaming.parse_streaming_multi_step import (
    parse_workflow_from_multistep_response,
)
from api_gpt.nlp.streaming.socket_announce import publish_data_to_socket
from api_gpt.nlp.streaming.streaming_simple import (
    request_chatgpt_streaming,
    simple_openai_call,
)
from api_gpt.utils import get_key_or_none, token_required
from api_gpt.workflows.db.apps_template import fill_intent_with_app_default_template
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.settings.debug import global_debug_flag
import re

EXPLORATION_SYSTEM_PROMPT_STREAMING = ""
with open("api_gpt/nlp/prompts/exploration_system_prompt_streaming.txt") as f:
    EXPLORATION_SYSTEM_PROMPT_STREAMING = f.read()

QUICK_SOFTWARES_MULTISTEP_PROMPT_SYSTEM = ""
with open("api_gpt/nlp/prompts/quick_exploration_multi_step.txt") as f2:
    try:
        QUICK_SOFTWARES_MULTISTEP_PROMPT_SYSTEM = f2.read()
    except Exception as e:
        print("failed in reading the exploration system prompt f2", e, flush=True)


def callback_multi_intent(
    response: str,
    text: str,
    user: str,
    workflow_data_result: map,
    workflow_id: str,
    end: bool,
) -> WorkflowData:
    try:
        workflow_data = parse_workflow_from_multistep_response(response, text)
        if workflow_data != None:
            workflow_data.id = workflow_id
            dumped_workflow = json.loads(MessageToJson(workflow_data))
            workflow_data_result["result"] = dumped_workflow
            if end:
                workflow_data_result["final_result"] = dumped_workflow
            publishing_data = {
                "workflow_data": dumped_workflow,
                "is_finished": end,
                "user": user,
            }
            publish_data_to_socket(publishing_data, user=user)
        return workflow_data, text
    except Exception as exception:
        workflow_data = WorkflowData()
        workflow_data.name = "Failed in converting: " + str(exception) + "  " + text
        return None, text


def add_software(app_name: str, workflow: WorkflowData):
    app_name = app_name.strip()
    if not app_name:
        return
    intent_data = workflow.intent_data.add()
    re.sub(r"^\d+\.\s*", "", app_name)
    app_name = app_name.strip(".")
    app_name = app_name.strip(" ")
    app_name = app_name.strip('"')
    app_name = app_name.strip("\n")
    intent_data.app_name = app_name
    intent_data.name = app_name

    intent_data.type = generate_intent_type_from_name(
        intent_data.name, intent_data.app_name, intent_data.api_url
    )
    intent_data.meta_data.MergeFrom(
        AppInfoHandler.getInstance().get_meta_data(
            intent_data.type, intent_data.app_name
        )
    )
    try:
        fill_intent_with_app_default_template(intent_data)
    except Exception as e:
        print("error in fill_intent_with_app_default_template ", e, flush=True)


def generate_quick_workflow_multi_step(text: str, workflow_id: str):
    workflow = WorkflowData()
    workflow.id = workflow_id
    workflow.name = text
    quick_response_system_prompt = ""
    quick_response_user_prompt = QUICK_SOFTWARES_MULTISTEP_PROMPT_SYSTEM.format(
        text=text
    )
    response = simple_openai_call(
        quick_response_user_prompt,
        system_prompt=quick_response_system_prompt,
        max_tokens=50,
    )
    keys = ["software:", "softwares:"]
    found = False
    for key in keys:
        if key in response.lower():
            found = True
            for line in response.split("\n"):
                if key in line.lower():
                    index = line.lower().find(key)
                    index += len(key)
                    softwares = line[index:]
                    for software in softwares.split(","):
                        software = software.strip()
                        add_software(software, workflow)
    if not found:
        for software in response.split(","):
            software = software.strip()
            add_software(software, workflow)
    return workflow


def request_quick_response_multi_step(text: str, user: str, workflow_id: str):
    workflow = generate_quick_workflow_multi_step(text, workflow_id)
    publishing_data = {
        "workflow_data": json.loads(MessageToJson(workflow)),
        "is_finished": False,
        "user": user,
    }
    publish_data_to_socket(publishing_data, user=user)


def perform_request_with_streaming_multi_step(
    text: str,
    user: str,
    workflow_id: str,
    max_tokens: int = 1000,
):
    try:
        workflow_data_result = {}
        system_prompt = EXPLORATION_SYSTEM_PROMPT_STREAMING
        user_prompt = f"Text: {text}"

        thread = Thread(
            target=request_quick_response_multi_step,
            args=(text, user, workflow_id),
        )
        thread.start()
        request_chatgpt_streaming(
            max_tokens,
            system_prompt,
            user_prompt,
            user,
            workflow_data_result,
            workflow_id,
            text,
            callback_multi_intent,
        )
        thread.join()
        if "final_result" in workflow_data_result:
            return workflow_data_result["final_result"], get_key_or_none(
                workflow_data_result, "response"
            )
        else:
            return get_key_or_none(workflow_data_result, "result"), get_key_or_none(
                workflow_data_result, "response"
            )
    except Exception as exception:
        return None, None
