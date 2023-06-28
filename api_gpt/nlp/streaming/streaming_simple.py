import json
from threading import Thread
from timeit import default_timer as timer
from typing import Optional

import openai
import requests
from google.protobuf.json_format import MessageToJson
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.integrations.app_info import AppInfoHandler
from api_gpt.nlp.exploration import generate_intent_type_from_name
from api_gpt.nlp.exploration_simple import (
    SINGLE_EXPLOR_SYSTEM_PROMPT,
    parse_json_from_string,
    parse_workflow_data_from_json,
)
from api_gpt.nlp.streaming.socket_announce import publish_data_to_socket
from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.utils import get_key_or_none, token_required


def request_chatgpt_streaming(
    max_tokens, system, content, user, workflow_data_result, workflow_id, text, callback
) -> Optional[map]:
    request = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": system,
            },
            {"role": "user", "content": content},
        ],
        "stream": True,
    }
    headers = {
        "Accept": "text/event-stream",
        "Authorization": "Bearer " + openai.api_key,
    }
    global start_timer
    start_timer = timer()
    openai_response = requests.post(
        url="https://api.openai.com/v1/chat/completions", headers=headers, json=request
    )

    client = sseclient.SSEClient(openai_response)
    response_str = ""
    for event in client.events():
        if event.data != "[DONE]":
            event_data = json.loads(event.data)
            if len(event_data["choices"]) == 0:
                continue
            choice = event_data["choices"][0]
            if "delta" not in choice:
                continue
            if "content" not in choice["delta"]:
                continue
            response_str += choice["delta"]["content"]
            callback(
                response_str,
                text,
                user,
                workflow_data_result,
                workflow_id,
                end=False,
            ),
        else:
            callback(
                response_str,
                text,
                user,
                workflow_data_result,
                workflow_id,
                end=True,
            ),


def request_gpt3_streaming(
    model, max_tokens, system_prompt, user_prompt
) -> Optional[map]:
    pass


def request_open_ai_with_streaming(
    system_prompt: str, user_prompt: str, model: str, max_tokens: int, callback
):
    pass


def callback_simple_intent(
    text: str,
    user: str,
    workflow_data_result: map,
    workflow_id: str,
    end: bool,
) -> WorkflowData:
    try:
        json_data = parse_json_from_string(text)
        workflow_data_result["response"] = text
    except Exception as exception:
        workflow_data = WorkflowData()
        workflow_data.name = "Failed in parsing: " + text
        return None, text
    try:
        workflow_data = parse_workflow_data_from_json(json_data, text)
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


def simple_openai_call(prompt: str, system_prompt: str = "", max_tokens: int = 30):
    try:
        response = get_openai_response_string(
            "gpt-3.5-turbo", max_tokens, system_prompt, prompt
        )
        print("openai quick response : ", response, flush=True)
        return response
    except Exception as exception:
        print("#### Error in simple openai call, ", exception, flush=True)
        return "Not found"


def generate_quick_workflow(text: str, workflow_id: str):
    quick_response_prompt = f"I want to {text}, what is the most relevant software can do this? limited to 1, do not output anything else. Find the most related software."
    response = simple_openai_call(quick_response_prompt)
    software = response.strip(".")
    software = software.strip(" ")
    software = software.strip("\n")
    workflow = WorkflowData()
    workflow.id = workflow_id
    workflow.name = text
    intent_data = workflow.intent_data.add()
    intent_data.app_name = software
    intent_data.name = software

    intent_data.type = generate_intent_type_from_name(
        intent_data.name, intent_data.app_name, intent_data.api_url
    )
    intent_data.meta_data.MergeFrom(
        AppInfoHandler.getInstance().get_meta_data(
            intent_data.type, intent_data.app_name
        )
    )
    return workflow


def request_quick_response(text: str, user: str, workflow_id: str):
    workflow = generate_quick_workflow(text, workflow_id)
    publishing_data = {
        "workflow_data": json.loads(MessageToJson(workflow)),
        "is_finished": False,
        "user": user,
    }
    publish_data_to_socket(publishing_data, user=user)


def perform_request_with_streaming(
    text: str,
    user: str,
    workflow_id: str,
    max_tokens: int = 1000,
):
    try:
        workflow_data_result = {}
        system_prompt = SINGLE_EXPLOR_SYSTEM_PROMPT
        user_prompt = f"Text: {text}"

        thread = Thread(
            target=request_quick_response,
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
            callback_simple_intent,
        )
        thread.join()
        print("workflow_data_result : ", workflow_data_result, flush=True)
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
