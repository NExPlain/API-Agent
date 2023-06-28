import datetime
import threading
import uuid
from copy import deepcopy
from typing import Optional, Tuple

from firebase_admin import credentials, db
from flask import current_app

from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.nlp.exploration import generate_email_reply_workflow_multistep
from api_gpt.nlp.exploration_template import EMAIL_REPLY_PROMPT_SYSTEM_TEMPLATE
from api_gpt.services.time_zones import get_current_iso_datetime
from api_gpt.settings.debug import global_debug_flag
from api_gpt.workflows.db.debrief_workflow import write_debrief_workflow
from api_gpt.workflows.generate_actions import generate_action_dict
from api_gpt.workflows.notification_context import NotificationContext


def generate_workflows(
    context: NotificationContext, force_rewrite: bool = False
) -> dict:
    if global_debug_flag:
        current_app.logger.debug(
            "start generate workflows for ", context.email_dict["subject"]
        )
    if not force_rewrite:
        try:
            old_action_dict_ref = db.reference(
                f"debrief/message_to_workflow/{context.user_id}/{context.email_dict['id']}"
            )
            old_action_dict = old_action_dict_ref.get()
            if old_action_dict != None and len(old_action_dict) > 0:
                if global_debug_flag:
                    current_app.logger.debug(
                        f"{context.email_dict['id']} already has actions: {old_action_dict}"
                    )
                return dict(old_action_dict)
        except Exception as e:
            current_app.logger.debug("error in generate_workflows : ", e)

    try:
        old_action_dict_ref = db.reference(
            f"debrief/message_to_workflow/{context.user_id}/{context.email_dict['id']}"
        )
        old_action_dict_ref.delete()
    except Exception as e:
        current_app.logger.debug("error in delete old workflows : ", e)
    action_dict = generate_action_dict(context)
    if global_debug_flag:
        current_app.logger.debug(
            "action dict for ", context.email_dict["subject"], action_dict
        )
    for action, action_prompt in action_dict.items():
        workflow_context = deepcopy(context)
        workflow_context.workflow_id = str(uuid.uuid4())
        thread = threading.Thread(
            target=generate_workflow_process,
            args=(workflow_context, action, action_prompt),
        )
        thread.start()
    return action_dict


def generate_email_reply_prompts(
    user_name: str,
    user_email: str,
    subject: str,
    email_from: str,
    email_to: str,
    action: str,
    content: str,
    debrief_context: str = "",
) -> Tuple[str, str]:
    debrief_context = debrief_context.replace("\n", " ")
    system_prompt = (
        f"Your name is {user_name}, email address is {user_email}. "
        + EMAIL_REPLY_PROMPT_SYSTEM_TEMPLATE
    )
    system_prompt = system_prompt.replace("{INFORMATION_PLACEHOLDER}", debrief_context)
    current_time = get_current_iso_datetime()
    time_prefix = f"Current time is {current_time}"
    if len(content) >= 1800:
        content = content[:1800]
    user_prompt = f"Subject: {subject}\nFrom: {email_from}\nTo: {email_to}\nContent: {content}\nAction: {action}, {time_prefix}."
    return system_prompt, user_prompt


# TODO: polish this
def generate_email_reply_action(
    context: NotificationContext,
    action_name: str,
    instruction: str,
    result: Optional[dict] = None,
) -> Tuple[Optional[WorkflowData], str]:
    """_summary_

    Args:
        context (NotificationContext): _description_
        action_name (str): _description_
        instruction (str): _description_
        result (Optional[dict], optional): _description_. Defaults to None.

    Returns:
        Tuple[Optional[WorkflowData], str]: _description_
    """
    system_prompt, user_prompt = generate_email_reply_prompts(
        user_name=context.user_name,
        user_email=context.user_email,
        subject=context.email_dict["subject"],
        email_from=context.email_dict["from"],
        email_to=context.email_dict["to"],
        action=instruction,
        content=context.email_dict["content"],
        debrief_context=context.context,
    )
    try:
        workflow_data, message = generate_email_reply_workflow_multistep(
            system_prompt, user_prompt, action_text=instruction
        )
    except Exception as e:
        current_app.logger.debug(
            "Error in generate_email_reply_workflow_multistep: ", e
        )
        return None, str(e)
    if result is not None:
        result[action_name] = workflow_data
    return workflow_data, message


def generate_workflow_process(
    context: NotificationContext, action_name: str, action_instruction: str
) -> Tuple[Optional[WorkflowData], str]:
    """_summary_

    Args:
        context (NotificationContext): _description_
        action_name (str): _description_
        action_instruction (str): _description_

    Returns:
        Tuple[Optional[WorkflowData], str]: _description_
    """
    workflow_data = WorkflowData()
    workflow_data.id = context.workflow_id
    workflow_data.create_timestamp = int(round(datetime.datetime.now().timestamp()))

    if global_debug_flag:
        current_app.logger.debug("write_debrief_workflow 1")
    write_debrief_workflow(
        user_id=context.user_id,
        message_id=context.email_dict["id"],
        action_name=action_name,
        workflow=workflow_data,
    )

    if global_debug_flag:
        current_app.logger.debug("generate_email_reply_action 1")
    workflow_data, message = generate_email_reply_action(
        context, action_name, action_instruction
    )
    if global_debug_flag:
        current_app.logger.debug("generate_email_reply_action 2")
    if global_debug_flag:
        if workflow_data is not None:
            current_app.logger.debug(
                "email reply action workflow_data ",
                workflow_data.id,
                len(workflow_data.intent_data),
            )
            current_app.logger.debug("message ", message)
        else:
            current_app.logger.debug(
                "workflow data is none for ",
                context.email_dict["subject"],
                action_instruction,
            )
    if workflow_data is not None:
        workflow_data.id = context.workflow_id
        workflow_data.create_timestamp = int(round(datetime.datetime.now().timestamp()))
        write_debrief_workflow(
            user_id=context.user_id,
            message_id=context.email_dict["id"],
            action_name=action_name,
            workflow=workflow_data,
        )
        return workflow_data, ""
    return None, "Generate failed"
