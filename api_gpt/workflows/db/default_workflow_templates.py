import json
import re
import uuid
from typing import List

from firebase_admin import credentials, db
from flask import current_app
from google.protobuf.json_format import Parse, ParseDict
from waiting import wait

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.intent_template_pb2 import IntentTemplate
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.data_structures.proto.generated.workflow_template_pb2 import (
    WorkflowTemplate,
)
from api_gpt.workflows.db.intent_template import get_intent_template_handler


def get_default_intent_from_template(intent_template: IntentTemplate) -> IntentData:
    intent_data = IntentData()
    intent_data.id = str(uuid.uuid4())
    intent_data.type = intent_template.type
    intent_data.name = intent_template.name
    intent_data.meta_data.MergeFrom(intent_template.meta_data)
    intent_data.oauth_endpoint = intent_template.oauth_endpoint
    intent_data.api_url = intent_template.execute_endpoint
    intent_data.app_name = intent_template.app_name
    for input in intent_template.inputs:
        intent_data.inputs.append(input)
    for output in intent_template.outputs:
        intent_data.outputs.append(output)
    return intent_data


def extract_name(input_string):
    # Define a regular expression pattern to match any icon or emoji at the beginning of the string
    pattern = r"^(/icon\{[^\}]+\}|[\U0001F000-\U0001F6FF])+"

    # Use the pattern to match any icon or emoji at the beginning of the string
    match = re.match(pattern, input_string)

    # If a match is found, remove the matched icon or emoji and any surrounding whitespace
    if match:
        input_string = input_string[len(match.group(0)) :].strip()

    # Return the resulting string, which should contain only the actual name
    return input_string


def parse_old_workflow_to_proto(old_workflow: map, name: str) -> WorkflowData:
    workflow_data = WorkflowData()
    workflow_data.name = name
    if "tasks" not in old_workflow:
        return None
    for task in old_workflow["tasks"]:
        intent = IntentData()
        for intent_attribute in task["intent_attributes"]:
            attribute_type = intent_attribute["intent_attribute_type"]
            if attribute_type == 4:
                continue
            content_json_str = intent_attribute["content"]
            content = json.loads(content_json_str)
            intent_templates_handler = get_intent_template_handler()
            if attribute_type == 0:  # intent select
                name = extract_name(content["selected"])
                type = intent_templates_handler.infer_intent_type_from_name(name)

                if type not in intent_templates_handler.intent_templates.keys():
                    continue

                intent_template = ParseDict(
                    intent_templates_handler.intent_templates[type], IntentTemplate()
                )

                intent.CopyFrom(get_default_intent_from_template(intent_template))
            elif attribute_type == 5:
                name = content["name"]
                value = content["text"]
                for input in intent.inputs:
                    if intent_templates_handler.is_name_match_parameter(
                        name, input.parameter.name
                    ):
                        input.parameter.value = value
            elif attribute_type == 1:
                name = content["name"]
                value = content["text"]
                for input in intent.inputs:
                    if intent_templates_handler.is_name_match_parameter(
                        name, input.parameter.name
                    ):
                        input.parameter.value = value
        if intent.type:
            workflow_data.intent_data.append(intent)
    return workflow_data


def get_default_workflow_template() -> List[WorkflowTemplate]:
    default_workflow_ref = db.reference(f"TestWorkspace2/workflows")
    workflows = default_workflow_ref.get()
    ret = []
    for key in workflows:
        old_template = workflows[key]
        workflow_template = WorkflowTemplate()
        workflow_template.name = old_template["name"]
        workflow_template.type = old_template["name"].lower().replace(" ", "_")
        if "description" in old_template:
            workflow_template.description = old_template["description"]
        base_workflow = old_template["base_workflow"]
        base_workflow_data = parse_old_workflow_to_proto(
            base_workflow, old_template["name"]
        )
        if base_workflow_data == None:
            continue
        for intent in base_workflow_data.intent_data:
            workflow_template.intents.append(intent)

        for example in old_template["examples"]:
            trigger_string = example["trigger_string"]
            workflow_data = parse_old_workflow_to_proto(
                example["workflow"], old_template["name"]
            )
            if workflow_data == None:
                continue
            workflow_example = workflow_template.examples.add()
            workflow_example.trigger_string = trigger_string
            workflow_example.workflow.CopyFrom(workflow_data)

        ret.append(workflow_template)
    return ret
