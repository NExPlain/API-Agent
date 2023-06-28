from typing import Tuple
from api_gpt.nlp.v1.generation import fetch_generate_v1_string
from api_gpt.nlp.exploration import generate_workflow_by_exploration
from api_gpt.nlp.generate_by_template import (
    generate_workflow_by_template,
    parse_string_response_to_workflow,
)
from api_gpt.nlp.parse import convert_json_response_to_workflow
from api_gpt.nlp.utils import extract_first_json
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from flask import request
from api_gpt.services.time_zones import get_current_iso_datetime
from api_gpt.utils import *
from api_gpt.nlp.prompt_templates import *
from google.protobuf.json_format import MessageToJson
from api_gpt.services.openai_request import *


def parse_response(content) -> Tuple[bool, WorkflowData]:
    try:
        json_object = extract_first_json(content)
        return True, convert_json_response_to_workflow(json_object)
    except Exception as exception:
        return False, "Failed in prasing " + str(exception)


def generate_ai_generation_v3(
    model: str, text: str, max_tokens: int
) -> Tuple[bool, WorkflowData]:
    """Genearete ai generation using v2 logic"""
    current_time = get_current_iso_datetime()

    system_prompt = SYSTEM_PROMPT_TEMPLATE_V3.format(current_time=current_time)
    user_prompt = USER_PROMPT_TEMPLATE_V3.format(text=text)

    json_response = {"message": "failed"}
    try:
        if model == "gpt-3.5-turbo":
            json_response = get_chat_gpt_response(
                max_tokens=max_tokens, system=system_prompt, content=user_prompt
            )
            if json_response == None:
                return False, "Failed to parse json response"
            response = json_response["choices"][0]["message"]["content"]
            return parse_response(response)
        else:
            json_response = get_gpt3_generation_result(
                model,
                max_tokens=1000,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            response = json_response["choices"][0]["text"]
            return parse_response(response)
    except Exception as exception:
        return False, str(exception)


def generate_without_template(
    current_time: str, text: str, max_tokens: int, model: str
):
    try:
        string_response = fetch_generate_v1_string(
            user_name="Plasma",
            user_id="plasma",
            email="hello@plasma.com",
            current_time=current_time,
            participants_string="",
            text=text,
            max_tokens=max_tokens,
            model=model,
        )
        if string_response == None:
            return None, "Generated string is None", 503
        return parse_string_response_to_workflow(string_response), "success", 200
    except Exception as exception:
        return None, str(exception), 505


def generate_workflow(
    text,
    model,
    max_tokens,
    use_template: bool,
    use_exploration: bool = False,
    user_context: str = "",
) -> Tuple[WorkflowData, str, int]:
    """_summary_

    Args:
        text (_type_): _description_
        model (_type_): _description_
        max_tokens (_type_): _description_
        use_template (bool): _description_

    Returns:
        Tuple[WorkflowData, str, int]: _description_
    """
    current_time = get_current_iso_datetime()
    if use_exploration:
        workflow_data, openai_response = generate_workflow_by_exploration(
            text, model, max_tokens, user_context=user_context
        )
        if workflow_data == None:
            print("retry", flush=True)
            workflow_data, openai_response = generate_workflow_by_exploration(
                text, model, max_tokens, user_context=user_context
            )

            if workflow_data == None:
                return None, openai_response, 505
            else:
                return workflow_data, "success", 200
        else:
            return workflow_data, "success", 200
    if use_template:
        try:
            workflow, error_message, error_code = generate_workflow_by_template(
                current_time=current_time, text=text, max_tokens=max_tokens, model=model
            )
            if workflow == None or "n/a" in workflow.name.lower():
                workflow_data, openai_response = generate_workflow_by_exploration(
                    text, model, max_tokens, user_context=user_context
                )
                if workflow_data == None:
                    return None, openai_response, error_code
                else:
                    return workflow_data, "success", 200
            return workflow, "success", 200
        except Exception as e:
            return generate_without_template(current_time, text, max_tokens, model)
    else:
        return generate_without_template(current_time, text, max_tokens, model)
