import uuid
from datetime import datetime
from typing import Optional, Tuple

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.parameter_pb2 import Parameter
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.data_structures.proto.generated.workflow_template_pb2 import (
    WorkflowTemplate,
)
from api_gpt.nlp.intent_utils import (
    fill_logo_or_emoji_for_intent,
    fill_parameter_type_and_logo,
    find_best_match_intent,
)
from api_gpt.nlp.prompt_template_2_steps import (
    build_identify_prompt_2_steps,
    build_parameter_prompt_2_steps,
)
from api_gpt.nlp.workflow_utils import get_workflow_data_from_template
from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.settings.debug import global_debug_flag
from api_gpt.workflows.db.default_workflow_templates import (
    get_default_workflow_template,
)
from api_gpt.workflows.db.workflow_template import get_workflow_template_handler


def parse_string_response_to_workflow(string_response: str) -> WorkflowData:
    workflow_data = WorkflowData()
    workflow_data.id = str(uuid.uuid4())
    for line in string_response.split("\n"):
        if "|" in line:
            # Task line
            sp = line.split("|")
            if len(sp) < 2:
                continue

            intent = find_best_match_intent(sp[0])
            if intent is None:
                continue
            intent_data = workflow_data.intent_data.add()

            parameters_string = sp[1].split("|")[0]
            if parameters_string.endswith("."):
                parameters_string = parameters_string[:-1]

            parameters_string = parameters_string.replace("(", "")
            parameters_string = parameters_string.replace(")", "")
            parameters_string = parameters_string.replace("[", "")
            parameters_string = parameters_string.replace("]", "")

            task_id = str(uuid.uuid4())
            intent_data.id = task_id
            intent_data.name = sp[0]
            intent_data.type = intent
            intent_data.create_timestamp = int(datetime.now().timestamp())
            fill_logo_or_emoji_for_intent(intent_data)

            parameters = parameters_string.split(": ")
            name = ""
            value = ""
            for i in range(len(parameters)):
                if i == 0:
                    name = parameters[i].strip()
                elif i == len(parameters) - 1:
                    value = parameters[i].strip()
                    if name == "":
                        continue
                    if (
                        value.startswith('"')
                        and value.endswith('"')
                        and len(value) >= 2
                    ):
                        value = value[1:-1]
                    input = intent_data.inputs.add()
                    input.parameter.name = name
                    input.parameter.value = value
                    fill_parameter_type_and_logo(input.parameter)
                else:
                    splits = parameters[i].split(", ")
                    if not splits:
                        continue
                    value = ", ".join(splits[:-1])
                    if name == "":
                        continue
                    if (
                        value.startswith('"')
                        and value.endswith('"')
                        and len(value) >= 2
                    ):
                        value = value[1:-1]
                    input = intent_data.inputs.add()
                    input.parameter.name = name
                    input.parameter.value = value
                    fill_parameter_type_and_logo(input.parameter)
                    name = splits[-1]
        elif "Name:" in line:
            workflow_data.name = line.split("Name:")[1].strip()
        elif "Summary:" in line:
            workflow_data.name = line.split("Summary:")[1].strip()
        elif "Summarize:" in line:
            workflow_data.name = line.split("Summarize:")[1].strip()
        elif "task:" in line:
            workflow_data.name = line.split("task:")[1].strip()
    return workflow_data


def parse_workflow_from_response(
    response: str, workflow_template: WorkflowTemplate
) -> WorkflowData:
    workflow_data = get_workflow_data_from_template(workflow_template)
    for line in response.split("\n"):
        attributeKv = line.split(": ")
        if len(attributeKv) == 2:
            keyName = attributeKv[0]
            valueName = attributeKv[1]
        else:
            keyName = attributeKv[0]
            valueName = ": ".join(attributeKv[1:])
        valueName = valueName.replace("\t", "\n")
        if valueName.startswith('"'):
            valueName = valueName[1:]
        if valueName.endswith('"'):
            valueName = valueName[:-1]
        for i in range(len(workflow_data.intent_data)):
            intent = workflow_data.intent_data[i]
            for input in intent.inputs:
                if keyName.lower().strip() == f"{i}.{input.parameter.name}":
                    input.parameter.value = valueName
    return workflow_data


def generate_workflow_by_template(
    current_time: str, text: str, max_tokens: int, model: str
) -> Tuple[Optional[WorkflowData], str, int]:
    if global_debug_flag:
        print("generate_workflow_by_template", flush=True)
    identify_prompts = build_identify_prompt_2_steps(
        text=text, current_time=current_time
    )
    # print('identify prompts : ', identify_prompts, flush=True)
    string_response = get_openai_response_string(
        model, max_tokens, identify_prompts[0], identify_prompts[1]
    )
    if string_response == None:
        return None, "Step 1 failed", 401
    if global_debug_flag:
        print(f"found string_response: {string_response}", flush=True)
    type = string_response
    if "." in type:
        index = type.find(".")
        type = type[index + 1 :]
        type = type.strip(" ")
        type = type.strip("\n")
        type = type.lower()
        type = type.replace(" ", "_")
    if global_debug_flag:
        print("type : ", type, flush=True)
    workflow_templates_handler = get_workflow_template_handler()
    workflow_template = workflow_templates_handler.get_workflow_template(type)
    parameter_prompts = build_parameter_prompt_2_steps(
        text=text, current_time=current_time, workflow_template=workflow_template
    )
    # print('parameter_prompts prompts : ', parameter_prompts, flush=True)
    string_response = get_openai_response_string(
        model, max_tokens, parameter_prompts[0], parameter_prompts[1]
    )
    try:
        workflow_data = parse_workflow_from_response(string_response, workflow_template)
    except Exception as exception:
        return None, "failed in workflow parsing " + exception, 502
    if workflow_data != None:
        return workflow_data, "success", 1
    else:
        return None, "failed in workflow parsing", 502
