import datetime
import json
import uuid
from threading import Thread
from typing import Optional, Tuple

from flask import Flask, current_app, jsonify, redirect, request, url_for
from google.protobuf.json_format import MessageToJson

from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.services.constants import CHATGPT_MODEL, DEFAULT_MAX_TOKENS
from api_gpt.settings.debug import global_debug_flag
from api_gpt.utils import get_key_or_default, token_required
from api_gpt.workflows.db.debrief_workflow import write_debrief_workflow
from api_gpt.workflows.generate_actions import GENERATE_DEBRIEF_ACTIONS_SYSTEM_PROMPT
from api_gpt.workflows.generate_workflow import (
    generate_email_reply_action,
    generate_email_reply_prompts,
    generate_workflow_process,
    generate_workflows,
)
from api_gpt.workflows.notification_context import NotificationContext


# TODO(lizhen): polish this
def get_email_reply_action_text(email_dict: dict, instruction: str):
    return f"""
        I got a email from to {email_dict['from']}, the subject is {email_dict['subject']}, content is {email_dict['content']}, and I want to handle it {instruction}.
    """


# TODO: implement this, now it alwahys return true
def query_is_email_action_needed(email_dict: dict) -> bool:
    return True


def generate_email_reply_actions(email_dict: dict) -> dict:
    is_action_needed = query_is_email_action_needed(email_dict)
    if not is_action_needed:
        name = "ignore"
        ignore_workflow_data = WorkflowData()
        ignore_workflow_data.id = email_dict["id"]
        ignore_workflow_data.name = name
        return {"id": email_dict["id"], "actions": {name: ignore_workflow_data}}
    reply_templates = {"positive": "in a positive way", "decline": "politely decline"}

    ret = {}
    threads = []
    for name, instruction in reply_templates.items():
        threads.append(
            Thread(
                target=generate_email_reply_action,
                args=(email_dict, name, instruction, ret),
            )
        )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return ret


@current_app.route("/email_reply_actions", methods=["POST"])
@token_required
def email_reply_actions():
    data = request.json
    try:
        email_dict = data["email"]
        ret = generate_email_reply_actions(email_dict)

        return {"message": "success", "status_code": 200, "data": ret}
    except Exception as e:
        return {
            "message": str(e),
            "status_code": 501,
        }


@current_app.route("/get_debrief_workflow_prompts", methods=["POST"])
@token_required
def get_debrief_workflow_prompts():
    data = request.json
    try:
        email_dict = data["email"]
        action_name = data["action_name"]
        user_name = data["user_name"]
        user_email = data["user_email"]
        debrief_context = get_key_or_default(data, "debrief_context", "")

        system_prompt, user_prompt = generate_email_reply_prompts(
            user_name=user_name,
            user_email=user_email,
            subject=email_dict["subject"],
            email_from=email_dict["from"],
            email_to=email_dict["to"],
            action=action_name,
            content=email_dict["content"],
            debrief_context=debrief_context,
        )

        return {
            "message": "success",
            "status_code": 200,
            "data": {"system_prompt": system_prompt, "user_prompt": user_prompt},
        }
    except Exception as e:
        return {
            "message": str(e),
            "status_code": 501,
        }


@current_app.route("/get_debrief_prompts", methods=["POST"])
@token_required
def get_debrief_prompts():
    data = request.json
    try:
        email_dict = data["email"]

        action_generation_system_prompt = GENERATE_DEBRIEF_ACTIONS_SYSTEM_PROMPT
        snippet = email_dict["content"]
        if len(snippet) >= 2000:
            snippet = snippet[:2000]
        action_generation_user_prompt = f"Subject: {email_dict['subject']}\nFrom: {email_dict['from']}\nSnippet: {snippet}\nActions: "

        return {
            "message": "success",
            "status_code": 200,
            "data": {
                "action_generation_system_prompt": action_generation_system_prompt,
                "action_generation_user_prompt": action_generation_user_prompt,
            },
        }
    except Exception as e:
        return {
            "message": str(e),
            "status_code": 501,
        }


@current_app.route("/email_reply_action", methods=["POST"])
@token_required
def email_reply_action():
    if global_debug_flag:
        current_app.logger.debug("email_reply_action")
    data = request.json
    try:
        email_dict = data["email"]
        action_name = data["action_name"]
        action_instruction = data["action_instruction"]
        workflow_id = data["workflow_id"]
        user_id = data["user_id"]
        user_name = data["user_name"]
        user_email = data["user_email"]
        debrief_context = get_key_or_default(data, "debrief_context", "")
        context = NotificationContext(
            email_dict, workflow_id, user_id, user_name, user_email, debrief_context
        )
        workflow_data, error_message = generate_workflow_process(
            context, action_name, action_instruction
        )
        if workflow_data != None:
            workflow_data_json = json.loads(MessageToJson(workflow_data))
            return {
                "message": "success",
                "status_code": 200,
                "data": workflow_data_json,
            }
        return {"message": error_message, "status_code": 303}
    except Exception as e:
        current_app.logger.debug("Exception in email_reply_action", e)
        return {
            "message": str(e),
            "status_code": 501,
        }


@current_app.route("/regenerate_workflows", methods=["POST"])
@token_required
def regenerate_workflows():
    if global_debug_flag:
        current_app.logger.debug("regenerate_workflows")
    data = request.json
    try:
        email_dict = data["email"]
        user_id = data["user_id"]
        user_name = data["user_name"]
        user_email = data["user_email"]
        debrief_context = get_key_or_default(data, "debrief_context", "")
        context = NotificationContext(
            email_dict,
            str(uuid.uuid4()),
            user_id,
            user_name,
            user_email,
            debrief_context,
        )
        generate_workflows(context, force_rewrite=True)
        return {"message": "success", "status_code": 200}
    except Exception as e:
        current_app.logger.debug("Exception in email_reply_action", e)
        return {
            "message": str(e),
            "status_code": 501,
        }
