from datetime import datetime
import json
from os import system
from tracemalloc import start
from typing import Tuple
from urllib import response
import uuid
from api_gpt.integrations.app_info import AppInfoHandler
from api_gpt.services.constants import CHATGPT_MODEL, DEFAULT_MAX_TOKENS
from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.nlp.classify import is_single_task
from api_gpt.nlp.exploration_simple import simple_task_exploration
from api_gpt.nlp.exploration_template import *
from api_gpt.nlp.intent_utils import (
    infer_parameter_icon_from_name,
    infer_parameter_type_from_name,
)
from api_gpt.nlp.utils import extract_first_json
from api_gpt.services.time_zones import get_current_iso_datetime
from api_gpt.utils import get_key_or_default
from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from google.protobuf.json_format import MessageToJson
from api_gpt.settings.debug import global_debug_flag, global_detailed_debug_flag
from timeit import default_timer as timer
import re
from flask import current_app

NEW_LINE_INDICATOR = "¬"


def fix_extracted_str(extracted_str):
    extracted_str = extracted_str.replace("\n", " ")
    # Fix the trailing comma
    extracted_str = re.sub(",[ \t\r\n]*}", "}", extracted_str)
    extracted_str = re.sub(",[ \t\r\n]*\]", "]", extracted_str)
    # extracted_str = extracted_str.replace('\"\"', '\"')
    extracted_str = extracted_str.strip()
    return extracted_str


def get_key_from_json(js, possible_keys, default_value=""):
    for key in possible_keys:
        if key in js:
            return js[key]
    return default_value


def get_substring_after_third_slash(input_string):
    slash_count = 0
    for index, char in enumerate(input_string):
        if char == "/":
            slash_count += 1
        if slash_count == 3:
            return input_string[index + 1 :]
    return input_string


def generate_intent_type_from_name(name, app_name, api_url):
    if api_url:
        suffix = get_substring_after_third_slash(api_url)
    else:
        suffix = ""
    raw_type = app_name + suffix
    raw_type = raw_type.lower()
    raw_type = raw_type.strip()
    raw_type = raw_type.strip("\n")
    raw_type = raw_type.replace("/", "_")
    raw_type = raw_type.replace(" ", "_")
    return raw_type


def extract_api_calls_faster(response_string: str):
    api_calls = []
    api_list = response_string.split("-----\n")[1:-1]

    for api in api_list:
        api_dict = {}
        lines = api.split("\n")[1:-1]
        for line in lines:
            key, value = line.split(": ")
            api_dict[key] = value.strip('"')
        api_calls.append(api_dict)
    return api_calls


def api_call_json_to_intent(api_call) -> IntentData:
    intent = IntentData()
    intent.id = str(uuid.uuid4())
    intent.app_name = get_key_from_json(api_call, ["app_name", "app name"], "API")
    intent.name = get_key_from_json(api_call, ["description"], api_call["app_name"])
    intent.api_url = get_key_from_json(api_call, ["endpoint_url", "end_point", ""])
    intent.type = generate_intent_type_from_name(
        intent.name, intent.app_name, intent.api_url
    )
    intent.meta_data.MergeFrom(
        AppInfoHandler.getInstance().get_meta_data(intent.type, intent.app_name)
    )
    for input in get_key_from_json(api_call, ["inputs", "input"], []):
        intent_input = intent.inputs.add()
        intent_input.parameter.name = input
        intent_input.parameter.type = infer_parameter_type_from_name(input)
        intent_input.parameter.icon = infer_parameter_icon_from_name(input)

    i = 0
    for input_value in get_key_from_json(api_call, ["input_value", "input_values"], []):
        if i < len(intent.inputs):
            intent.inputs[i].parameter.value = str(
                input_value.replace(NEW_LINE_INDICATOR, "\n")
            )
        i += 1
    for output in get_key_from_json(api_call, ["outputs", "output"], []):
        intent_output = intent.outputs.add()
        intent_output.parameter.name = output
        intent_output.parameter.type = infer_parameter_type_from_name(output)
        intent_output.parameter.icon = infer_parameter_icon_from_name(output)
    return intent


def parse_exploration_response_faster(response_string: str, text: str) -> WorkflowData:
    workflow = WorkflowData()
    try:
        api_calls = extract_api_calls_faster(response_string)
    except Exception as e:
        return None
    workflow.name = text
    for api_call in api_calls:
        workflow.intent_data.append(api_call_json_to_intent(api_call))
    return workflow


def parse_exploration_response(response_string: str, text: str) -> WorkflowData | None:
    workflow = WorkflowData()
    if "[" not in response_string:
        workflow.name = response_string
        return workflow
    start_index = response_string.find("[")
    end_index = response_string.rfind("]")
    try:
        api_calls_str = fix_extracted_str(response_string[start_index : end_index + 1])
    except Exception as e:
        print("Error in fix_extracted_str : ", e)
        return None
    try:
        if global_detailed_debug_flag:
            print("### api_calls_str : ", api_calls_str, flush=True)
        api_calls = json.loads(api_calls_str)
    except Exception as e:
        print(f"Error in json parsing : {str(e)}")
        return None
    workflow.name = text
    for api_call in api_calls:
        try:
            workflow.intent_data.append(api_call_json_to_intent(api_call))
        except Exception as e:
            print("Error in parse api_call_json_to_intent")
    return workflow


def parse_response_bruteforce(response: str, text: str) -> WorkflowData:
    possible_separaters = ["---", "```", "==="]
    for separaters in possible_separaters:
        if separaters in response:
            apis = []
            separater_c = separaters[0]
            start_index = 0
            num_api = 1
            while start_index < len(response) and separaters in response[start_index:]:
                start_index = response.find(separaters, start_index) + len(separaters)
                while (
                    start_index < len(response) and response[start_index] == separater_c
                ):
                    start_index += 1
                if start_index >= len(response):
                    continue
                end_index = response.find(separaters, start_index + 1)
                api_calls = fix_extracted_str(response[start_index:end_index])
                if len(api_calls.strip()) == 0:
                    continue
                try:
                    if api_calls[0] == "{":
                        if (
                            f"apicall {num_api}" in response.lower()
                            or f"apicall{num_api}" in response.lower()
                        ):
                            single_api = json.loads(api_calls)
                            apis.append(single_api)
                    elif api_calls[0] == "[":
                        if len(apis) == 0:
                            api_calls = fix_extracted_str(api_calls)
                            apis = json.loads(api_calls)
                except Exception as exception:
                    if global_debug_flag:
                        print("Error in parsing : ", exception, flush=True)
                num_api += 1
            workflow = WorkflowData()
            workflow.name = str(text)
            for api_call in apis:
                try:
                    workflow.intent_data.append(api_call_json_to_intent(api_call))
                except Exception as exception:
                    if global_debug_flag:
                        print(
                            "Error in parsing intent : ",
                            exception,
                            api_call,
                            flush=True,
                        )
                    continue

            return workflow
    return None


def parse_by_openai(model, max_tokens, response, text) -> WorkflowData:
    try:
        response_string = get_openai_response_string(
            model, max_tokens, "", REPARSE_TEMPLATE + "\n" + response
        )
        response_string = extract_first_json(response_string)

        workflow_data = parse_exploration_response(response, text)
        if workflow_data == None:
            workflow_data = parse_response_bruteforce(response, text)
        return workflow_data
    except Exception as exception:
        print(
            f"parse by openai failed : {exception}, response : {response}", flush=True
        )
        return None


def generate_email_reply_workflow_multistep(
    system_prompt, user_prompt, action_text
) -> Tuple[WorkflowData, str]:
    """_summary_

    Args:
        system_prompt (_type_): _description_
        user_prompt (_type_): _description_
        action_text (_type_): _description_

    Returns:
        Tuple[WorkflowData, str]: _description_
    """
    response = get_openai_response_string(
        CHATGPT_MODEL, DEFAULT_MAX_TOKENS, system_prompt, user_prompt
    )
    if global_detailed_debug_flag:
        print(f"### system_prompt string : {system_prompt}", flush=True)
        print(f"### user_prompt string : {user_prompt}", flush=True)
        print(f"### response string : {response}", flush=True)
        pass
    if global_debug_flag:
        print(f"### response string : {response}", flush=True)
    if response == None:
        return None, response
    # print('### response : ', response, flush=True)
    try:
        workflow_data = parse_exploration_response(response, action_text)
    except Exception as e:
        print("Error in parse_exploration_response : ", e)
    if workflow_data == None or len(workflow_data.intent_data) == 0:
        workflow_data = parse_response_bruteforce(response, action_text)
        if workflow_data == None or len(workflow_data.intent_data) == 0:
            workflow_data = parse_by_openai(
                CHATGPT_MODEL, DEFAULT_MAX_TOKENS, response, action_text
            )
    if global_debug_flag:
        print(workflow_data, flush=True)
    if workflow_data == None:
        return None, response
    # print('### workflow_data : ', MessageToJson(workflow_data), flush=True)
    return workflow_data, response


def generate_workflow_by_exploration(
    text, model, max_tokens, user_context: str = ""
) -> Tuple[WorkflowData, str]:
    start = timer()
    is_simple_task = is_single_task(text, model, max_tokens)
    end = timer()
    if global_debug_flag:
        seconds = int((end - start) * 10) / 10
        print(f"Classification step took {seconds} seconds", flush=True)
    if is_simple_task:
        start = timer()
        workflow, openai_response = simple_task_exploration(
            text, model, max_tokens, user_context=user_context
        )
        end = timer()
        seconds = int(end - start)
        if global_debug_flag:
            print(f"single step generartion took {seconds} seconds", flush=True)
            print(f"openai_response : {openai_response}", flush=True)
        if workflow != None:
            return workflow, openai_response
    current_time = get_current_iso_datetime()
    time_prefix = f"Current time is {current_time}"
    system_prompt = EXPLORATION_PROMPT_SYSTEM_TEMPLATE
    system_prompt = time_prefix + ", " + system_prompt
    user_prompt = EXPLORATION_PROMPT_USER_TEMPLATE.format(text=text)
    user_prompt += f", current time is {current_time}."

    default_context = "Rose (Meitong) Li is the CEO of Plasma AI, her email is meitongli.rose@gmail.com, Zhen Li is the CTO of Plasma AI, his email is lizhenpi@gmail.com."
    context_str = f'You will generate based on these context : "{default_context} {user_context}"\n'
    user_prompt = context_str + user_prompt
    response = get_openai_response_string(model, max_tokens, system_prompt, user_prompt)
    if global_debug_flag:
        print(f"### response string : {response}", flush=True)
        pass
    if response == None:
        return None, response
    # print('### response : ', response, flush=True)
    workflow_data = parse_exploration_response(response, text)
    if workflow_data == None:
        workflow_data = parse_response_bruteforce(response, text)
        if workflow_data == None:
            workflow_data = parse_by_openai(model, max_tokens, response, text)
    if global_debug_flag:
        print(workflow_data, flush=True)
    if workflow_data == None:
        return None, response
    # print('### workflow_data : ', MessageToJson(workflow_data), flush=True)
    return workflow_data, response
