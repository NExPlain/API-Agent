import json
from typing import List

from firebase_admin import credentials, db
from flask import jsonify, request
from google.protobuf.json_format import MessageToJson
from api_gpt.integrations.app_info import AppInfoHandler
from api_gpt.integrations.firebase import init_firebase
from api_gpt.nlp.intent_utils import (
    infer_parameter_icon_from_name,
    infer_parameter_type_from_name,
)
from api_gpt.utils import token_required

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.intent_template_pb2 import IntentTemplate
from flask import current_app


def init_intent_templates_handler(testing_environment: bool = False):
    instance = IntentTemplatesHandler.initInstance(
        testing_environment=testing_environment
    )
    if not testing_environment:
        instance.get_intent_templates_route()
        instance.write_intent_templates_route()


class IntentTemplatesHandler:
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
            raise ValueError("IntentTemplatesHandler instance is not initialized")
        return cls._instance

    def __init__(self, init_with_data: bool = False):
        self.intent_templates_ref_path = f"plasma/app_info/intent_templates"
        self.intent_templates = {}
        self.is_intent_templates_init = False
        if init_with_data:
            self.intent_templates_ref = db.reference(self.intent_templates_ref_path)
            self.initialize_intent_templates()
            self.intent_templates_ref.listen(self.intent_template_listener)
        else:
            self.is_intent_templates_init = True

    def is_name_match_parameter(self, name: str, parameter_name: str) -> bool:
        return name == parameter_name

    def infer_intent_type_from_name(self, name: str) -> str:
        name = name.lower().replace(" ", "_")
        if name == "send_email":
            return "send_gmail"
        elif name == "book_meeting":
            return "book_meeting_google"
        elif name == "create_slide":
            return "create_google_slide"
        elif name == "auto_response":
            return "gmail_auto_response"
        elif name == "create_tweet":
            return "create_tweet"
        elif name == "send_message":
            return "send_slack_message"
        elif name == "assign_task":
            return "assign_a_task"
        return name.lower().replace(" ", "_")

    def add_input(
        self,
        intent_template: IntentTemplate | IntentData,
        name: str,
        type: str | None = None,
        icon: str | None = None,
        value: str | None = None,
    ):
        input = intent_template.inputs.add()
        input.parameter.name = name
        if type == None:
            type = infer_parameter_type_from_name(name)
        if icon == None:
            icon = infer_parameter_icon_from_name(name)
        if value == None:
            value = name
        input.parameter.type = type
        input.parameter.icon = icon
        input.parameter.value = value

    def add_output(
        self,
        intent_template: IntentTemplate | IntentData,
        name: str,
        type: str | None,
        icon: str | None,
        value: str | None,
    ):
        output = intent_template.outputs.add()
        if type == None:
            type = infer_parameter_type_from_name(name)
        if icon == None:
            icon = infer_parameter_icon_from_name(name)
        if value == None:
            value = name
        output.parameter.name = name
        output.parameter.type = type
        output.parameter.icon = icon
        output.parameter.value = value

    def intent_template_listener(self, event):
        global intent_templates
        # print('### intent_template_listener : ', event.data, flush=True)
        # intent_templates = event.data

    def get_gmail_intent_template(self) -> IntentTemplate:
        template = IntentTemplate()
        template.type = "send_gmail"
        template.name = "Send email"
        template.app_name = "Gmail"
        template.meta_data.MergeFrom(
            AppInfoHandler.getInstance().get_meta_data(template.type, template.app_name)
        )
        template.oauth_endpoint = (
            f"https://memology-demo.herokuapp.com/integration/{template.type}/login"
        )
        template.execute_endpoint = "123"
        self.add_input(template, "to", "short_string", "people", "zhenli@plasma-doc.ai")
        self.add_input(template, "to", "short_string", "people", "zhenli@plasma-doc.ai")
        self.add_input(template, "title", "long_string", "title", "Hello from Plasma")
        self.add_input(
            template,
            "content",
            "long_string",
            "content",
            "Hello, this is a auto generated email from plasma",
        )
        return template

    def get_book_meeting_intent_template(
        self,
    ) -> IntentTemplate:
        template = IntentTemplate()
        template.type = "book_meeting_google"
        template.name = "Book Meeting"
        template.app_name = "Google Calendar"
        template.meta_data.MergeFrom(
            AppInfoHandler.getInstance().get_meta_data(template.type, template.app_name)
        )
        template.oauth_endpoint = (
            f"https://memology-demo.herokuapp.com/integration/{template.type}/login"
        )
        template.execute_endpoint = ""
        self.add_input(
            template, "participants", "short_string", "people", "zhenli@plasma-doc.ai"
        )
        self.add_input(
            template, "agenda", "short_string", "content", "Intro meeting to Plasma"
        )
        self.add_input(
            template, "start time", "time", "time", "2023-03-15T15:00:00.894"
        )
        self.add_input(template, "end time", "time", "time", "2023-03-15T15:30:00.894")
        return template

    def create_intent_data(
        self,
        name: str,
        app_name: str,
        api_url: str,
        inputs: list,
        outputs: list,
        values: list = [],
    ):
        intent_data = IntentData()
        lowercase_name = name.lower().replace(" ", "_")
        intent_data.type = lowercase_name
        intent_data.name = name
        intent_data.app_name = app_name
        intent_data.meta_data.MergeFrom(
            AppInfoHandler.getInstance().get_meta_data(
                intent_data.type, intent_data.app_name
            )
        )
        intent_data.oauth_endpoint = (
            f"https://memology-demo.herokuapp.com/integration/{lowercase_name}/login"
        )
        intent_data.api_url = api_url
        i = 0
        for input in inputs:
            value = None
            if i < len(values):
                value = values[i]
            i += 1
            self.add_input(intent_data, input, type=None, icon=None, value=str(value))
        for output in outputs:
            self.add_output(intent_data, output, type=None, icon=None, value=None)
        return intent_data

    def create_intent(
        self, name: str, app_name: str, inputs: list, outputs: list, values: list = []
    ):
        template = IntentTemplate()
        lowercase_name = name.lower().replace(" ", "_")
        template.type = lowercase_name
        template.name = name
        template.app_name = app_name
        template.meta_data.MergeFrom(
            AppInfoHandler.getInstance().get_meta_data(template.type, template.app_name)
        )
        template.oauth_endpoint = (
            f"https://memology-demo.herokuapp.com/integration/{lowercase_name}/login"
        )
        template.execute_endpoint = (
            f"https://memology-demo.herokuapp.com/integration/workflow/execute"
        )
        i = 0
        for input in inputs:
            value = None
            if i < len(values):
                value = values[i]
            i += 1
            self.add_input(template, input, type=None, icon=None, value=value)
        for output in outputs:
            self.add_output(template, output, type=None, icon=None, value=None)
        return template

    # Send email, with parameters: title, content, and recipient.
    # Book meetings, with parameters: start time, end time, agenda and participants.
    # Send slack messages, with parameters: receiver and message content.
    # Assign a task, with parameters: task, content and assignee.
    # Create page posts in facebook pages, with parameters: page, message.
    # Create Tweets in Twitter, with parameters: message.
    # Create or Append to Text File in Dropbox, with parameters: folder, file name, content.
    # Create Record in Salesforce, with parameters: name, content.
    # Upload file to Google drive, with parameters: file name.
    # Create Google slide, with parameters: title, topic, detailed script.
    # Create a reminder, with parameters: time, assignee, topic.
    # Create a email auto response, with parameters: start time, end time, content.
    # Apply PTO on workday, with parameters: start time, end time.
    # Create a github issue, with parameters: repository, title, body, assignee.
    def generate_default_intents(
        self,
    ) -> List[IntentTemplate]:
        return [
            self.create_intent(
                "Send slack message",
                "Slack",
                inputs=["receiver", "message", "channel"],
                outputs=["content"],
            ),
            self.create_intent(
                "Assign a task",
                "Plasma",
                inputs=["task", "content", "assignee"],
                outputs=[],
            ),
            self.create_intent(
                "Create Google slide",
                "Google Slide",
                inputs=["title", "topic", "detailed script"],
                outputs=["slide_link"],
            ),
            self.create_intent(
                "Create a reminder",
                "Plasma",
                inputs=["time", "assignee", "topic"],
                outputs=["reminder link"],
            ),
            self.create_intent(
                "Create a github issue",
                "Github",
                inputs=["repository", "title", "body", "assignee"],
                outputs=["issue_link"],
            ),
            self.create_intent(
                "Gmail Auto response",
                "Gmail",
                inputs=["start_time", "end_time", "title", "content"],
                outputs=[""],
            ),
            self.create_intent(
                "Create tweet", "Twitter", inputs=["content"], outputs=["tweet_link"]
            ),
        ]

    def write_intent_template(self, intent_template: IntentTemplate):
        type = intent_template.type
        intent_template_json = json.loads(MessageToJson(intent_template))

        global intent_templates
        self.intent_templates[type] = intent_template_json
        messages_ref = db.reference(f"{self.intent_templates_ref_path}/{type}")
        messages_ref.set(intent_template_json)

    def initialize_intent_templates(
        self,
    ):
        self.write_intent_template(self.get_gmail_intent_template())
        self.write_intent_template(self.get_book_meeting_intent_template())
        for intent_template in self.generate_default_intents():
            self.write_intent_template(intent_template)
        global intent_templates
        messages = self.intent_templates_ref.get()
        if messages:
            intent_templates = messages
        else:
            intent_templates = {}
        self.is_intent_templates_init = True

    def get_intent_templates_route(self):
        try:

            @current_app.route("/get_intent_templates", methods=["POST"])
            @token_required
            def get_intent_templates():
                return intent_templates

        except Exception as e:
            pass

    def write_intent_templates_route(self):
        try:

            @current_app.route("/write_intent_templates", methods=["POST"])
            @token_required
            def write_messages():
                type = request.json.get("type", "test")

                intent_template = IntentTemplate()
                intent_template.type = type
                intent_template.name = "Test intent"
                self.write_intent_template(intent_template=intent_template)

                return jsonify({"status": intent_templates})

        except Exception as e:
            pass


def get_intent_template_handler() -> IntentTemplatesHandler:
    return IntentTemplatesHandler.getInstance()
