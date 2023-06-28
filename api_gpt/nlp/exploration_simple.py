import json
import uuid
from datetime import datetime
from typing import Tuple

from flask import current_app

from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.services.time_zones import get_current_iso_datetime
from api_gpt.workflows.db.intent_template import IntentTemplatesHandler

SINGLE_EXPLOR_SYSTEM_PROMPT = ""

with open("api_gpt/nlp/prompts/exploration_system_prompt_single.txt") as f:
    SINGLE_EXPLOR_SYSTEM_PROMPT = f.read()


def parse_string_list(value: str):
    try:
        parsed_json = json.loads(value)
        return parsed_json
    except Exception as e:
        pass

    ret = []
    value = value.strip("[")
    value = value.strip("]")
    values = value.split(",")
    for x in values:
        x = x.strip()
        x = x.strip('"')
        ret.append(x)
    return ret


def parse_json_from_string(response: str):
    if "]" in response:
        response = response[: response.rfind("]") + 1]
    ret = {}
    for line in response.split("\n"):
        if ": " not in line:
            continue
        try:
            index = line.find(": ") + len(": ")
            key = line[: index - 2]
            val = line[index:]
        except:
            continue
        key = key.strip()
        val = val.strip()
        key = key.strip(",")
        val = val.strip(",")
        key = key.strip('"')
        if (
            key == "inputs"
            or key == "values"
            or key == "input_values"
            or key == "outputs"
        ):
            try:
                val = val.strip('"')
                val = val.strip("'")
                ret[key] = parse_string_list(val)
            except:
                continue
        else:
            try:
                if "POST " in val:
                    val = val.replace("POST ", "")
                val = val.strip()
                val = val.strip("\n")
                # Only return the complete app_name as it disturbs the logo
                if key == "app_name" and len(val) > 0 and val[-1] != '"':
                    continue
                ret[key] = val.strip('"')
            except:
                continue
    return ret


def get_value_or_default(json_data, names, default):
    for name in names:
        if name in json_data:
            return json_data[name]
    return default


def parse_workflow_data_from_json(json_data, workflow_name) -> WorkflowData | None:
    # The parsed app has to have some name
    name = get_value_or_default(
        json_data,
        [
            "app_name",
            "app name",
        ],
        "",
    )
    if not name:
        return None
    workflow_data = WorkflowData()
    workflow_data.name = workflow_name
    intent = workflow_data.intent_data.add()
    intent.id = str(uuid.uuid4())
    intent.MergeFrom(
        IntentTemplatesHandler.getInstance().create_intent_data(
            get_value_or_default(
                json_data,
                [
                    "name",
                    "description",
                ],
                "",
            ),
            name,
            get_value_or_default(
                json_data,
                [
                    "api",
                    "api",
                ],
                "",
            ),
            get_value_or_default(
                json_data,
                [
                    "inputs",
                    "input",
                ],
                [],
            ),
            [],
            get_value_or_default(
                json_data,
                ["values", "value", "input_values"],
                [],
            ),
        )
    )
    return workflow_data


def simple_task_exploration(
    text: str, model: str, max_tokens: str, user_context: str = ""
) -> Tuple[WorkflowData, str]:
    system_prompt = SINGLE_EXPLOR_SYSTEM_PROMPT
    current_time = get_current_iso_datetime()
    default_context = "Rose (Meitong) Li is the working on Plasma AI, her email is meitongli.rose@gmail.com, Zhen Li is working on Plasma AI, his email is lizhenpi@gmail.com."
    context_str = (
        f'You will generate based on these context : "{default_context} {user_context}"'
    )
    user_prompt = f'"{context_str}.\nText: {text}, current time is {current_time}.'
    string_response = get_openai_response_string(
        model, max_tokens, system_prompt, user_prompt
    )
    try:
        json_data = parse_json_from_string(string_response)
    except Exception as exception:
        workflow_data = WorkflowData()
        workflow_data.name = "Failed in parsing: " + string_response
        return workflow_data, string_response
    try:
        return parse_workflow_data_from_json(json_data, text), string_response
    except Exception as exception:
        workflow_data = WorkflowData()
        workflow_data.name = (
            "Failed in converting: " + str(exception) + "  " + string_response
        )
        return workflow_data, string_response
