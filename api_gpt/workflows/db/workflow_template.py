import json
from typing import List

from firebase_admin import db
from flask import Flask, current_app, jsonify, request
from google.protobuf.json_format import MessageToJson, Parse, ParseDict

from api_gpt.data_structures.proto.generated.workflow_template_pb2 import (
    WorkflowTemplate,
)
from api_gpt.workflows.db.default_workflow_templates import (
    get_default_workflow_template,
)
from api_gpt.workflows.db.intent_template import *


class WorkflowTemplateHandler:
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
            raise ValueError("WorkflowTemplateHandler instance is not initialized")
        return cls._instance

    def __init__(self, init_with_data: bool = True):
        self.workflow_templates = {}
        if init_with_data:
            self.workflow_templates_ref = db.reference(f"workflow_templates")
            self.initialize_workflow_templates()
            self.workflow_templates_ref.listen(self.workflow_template_listener)
            self.get_workflow_templates_route()

    def workflow_template_listener(self, event):
        self.workflow_templates = event.data

    def write_workflow_template(self, workflow_template: WorkflowTemplate):
        type = workflow_template.type
        workflow_template_json = json.loads(MessageToJson(workflow_template))

        self.workflow_templates[type] = workflow_template_json
        messages_ref = db.reference(f"workflow_templates/{type}".format(type))
        messages_ref.set(workflow_template_json)

    def initialize_workflow_templates(self):
        for workflow_template in get_default_workflow_template():
            self.write_workflow_template(workflow_template)

        messages = self.workflow_templates_ref.get()
        if messages:
            self.workflow_templates = messages
        else:
            self.workflow_templates = {}

    def get_workflow_template(self, type):
        workflow_template_json = self.workflow_templates[type]
        return ParseDict(workflow_template_json, WorkflowTemplate())

    def get_workflow_templates_route(self):
        try:

            @current_app.route("/get_workflow_templates", methods=["POST"])
            @token_required
            def get_workflow_templates():
                return jsonify({"status": self.workflow_templates})

        except Exception as exception:
            pass


def init_workflow_template_handler(testing_environment: bool = False):
    WorkflowTemplateHandler.initInstance(testing_environment=testing_environment)


def get_workflow_template_handler() -> WorkflowTemplateHandler:
    return WorkflowTemplateHandler.getInstance()
