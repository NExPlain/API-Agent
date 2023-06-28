import json
from typing import List

from firebase_admin import db
from flask import current_app
from google.protobuf.json_format import MessageToJson, ParseDict

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.intent_input_pb2 import IntentInput
from api_gpt.data_structures.proto.generated.intent_output_pb2 import IntentOutput
from api_gpt.data_structures.proto.generated.intent_template_pb2 import IntentTemplate
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.workflows.db.utils import convert_to_intent_template


class AppsTemplateHandler:
    _instance = None
    _testing_environment = False

    @classmethod
    def initInstance(cls, testing_environment: bool = False):
        if cls._instance is None:
            cls._testing_environment = testing_environment
            cls._instance = cls(
                init_with_data=not testing_environment,
            )
        return cls._instance

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            raise ValueError("AppsTemplateHandler instance is not initialized")
        return cls._instance

    def __init__(self, init_with_data: bool = True):
        self.apps_templates_ref_path = f"plasma/app_info/apps_templates"
        self.is_apps_templates_init = False
        self.apps_templates = {}
        if init_with_data:
            self.apps_templates_ref = db.reference(self.apps_templates_ref_path)
            self.initialize_apps_templates()
            self.apps_templates_ref.listen(self.apps_template_listener)

    def apps_template_listener(self, event):
        # print('### apps_template_listener : ', event.data, flush=True)
        # self.apps_templates = event.data
        pass

    def normalize_app_name(self, app_name):
        return (
            app_name.lower()
            .replace(" ", "_")
            .replace("@", "_")
            .replace(".", "_")
            .replace("/", "_")
        )

    def dump_template_from_generated_workflow(self, workflow_data: WorkflowData):
        for intent in workflow_data.intent_data:
            app_name = self.normalize_app_name(intent.app_name)
            if app_name in self.apps_templates:
                continue
            intent_template = convert_to_intent_template(intent)
            self.write_apps_template(intent_template)

    def fill_intent_with_app_default_template(self, intent_data: IntentData):
        app_name = intent_data.app_name
        type = self.normalize_app_name(intent_data.app_name)
        if type not in self.apps_templates:
            return
        app_template = self.apps_templates[type]
        if app_template is None:
            return
        for input in app_template.inputs:
            add_input = IntentInput()
            add_input.MergeFrom(input)
            add_input.parameter.value = ""
            intent_data.inputs.append(add_input)
        for output in app_template.outputs:
            add_output = IntentOutput()
            add_output.MergeFrom(output)
            add_output.parameter.value = ""
            intent_data.outputs.append(add_output)
        intent_data.api_url = app_template.execute_endpoint

    def write_apps_template(self, apps_template: IntentTemplate):
        app_name = self.normalize_app_name(apps_template.app_name)
        if app_name in self.apps_templates:
            return
        if len(apps_template.inputs) == 0:
            return
        self.apps_templates[app_name] = apps_template
        apps_template_json = json.loads(MessageToJson(apps_template))

        messages_ref = db.reference(f"{self.apps_templates_ref_path}/{app_name}")
        messages_ref.set(apps_template_json)

    def initialize_apps_templates(self):
        messages = self.apps_templates_ref.get()
        if messages:
            for k, v in messages.items():
                try:
                    intent_template = ParseDict(v, IntentTemplate())
                    self.apps_templates[k] = intent_template
                except Exception as exception:
                    pass
        else:
            self.apps_templates = {}
        self.is_apps_templates_init = True


def init_app_template_handler(testing_environment: bool = False):
    AppsTemplateHandler.initInstance(testing_environment=testing_environment)


def get_app_template_handler() -> AppsTemplateHandler:
    return AppsTemplateHandler.getInstance()
