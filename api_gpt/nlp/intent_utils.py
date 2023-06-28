from typing import Optional

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.parameter_pb2 import Parameter
from api_gpt.integrations.app_info import AppInfoHandler


def fill_logo_or_emoji_for_intent(intent_data: IntentData):
    intent_data.meta_data.MergeFrom(
        AppInfoHandler.getInstance().get_meta_data(
            intent_data.type, intent_data.app_name
        )
    )


def infer_parameter_type_from_name(key: str):
    name = key.lower()
    if "time" in name or name == "start" or name == "end" or "due" in name:
        return "time"
    if "content" in name or "message" in name or "agenda" in name or "body" in name:
        return "long_string"
    if "file" in name:
        return "file"
    return "short_string"


def infer_parameter_icon_from_name(key: str):
    name = key.lower()
    if "time" in name or name == "start" or name == "end":
        return "time"
    if "participant" in name or "people" in name:
        return "people"
    if "file" in name:
        return "file"
    return "content"


def get_parameter_emoji(textbox_name):
    switcher = {
        "assignee": "🥷",
        "list": "📋",
        "start time": "⌚",
        "time": "⌚",
        "end time": "⌚",
        "meeting time": "⌚",
        "reminder time": "⌚",
        "agenda": "📓",
        "link": "🔗",
        "google drive url": "🔗",
        "url": "🔗",
        "table": "📊",
        "receiver": "🥷",
        "participant": "🥷",
        "participants": "🥷",
        "recipient": "🥷",
        "recipients": "🥷",
        "file": "📃",
        "file name": "🖊️",
        "title": "🖊️",
        "notes": "📒",
        "attachment": "📄",
        "email": "📧",
    }
    return switcher.get(textbox_name.lower(), "📝")


def get_parameter_icon(textbox_name):
    switcher = {
        "assignee": "people",
        "list": "list",
        "start time": "time",
        "time": "time",
        "end time": "time",
        "meeting time": "time",
        "reminder time": "time",
        "agenda": "content",
        "link": "link",
        "google drive url": "link",
        "url": "link",
        "table": "table",
        "receiver": "people",
        "participant": "people",
        "participants": "people",
        "recipient": "people",
        "recipients": "people",
        "file": "file",
        "file name": "file",
        "title": "title",
        "notes": "content",
        "attachment": "attachment",
        "email": "email",
    }
    return switcher.get(textbox_name.lower(), "content")


def fill_parameter_type_and_logo(parameter: Parameter):
    parameter.type = infer_parameter_type_from_name(parameter.name)
    parameter.emoji = get_parameter_emoji(parameter.name)
    parameter.icon = get_parameter_icon(parameter.name)


def find_best_match_intent(name: str) -> Optional[str]:
    name = name.strip()
    if ". " in name:
        name = name.split(". ")[1].strip()
    name = name.lower().strip()
    if "email" in name:
        return "send_gmail"
    elif "meeting" in name:
        return "book_meeting_google"
    elif "assign" in name and "task" in name:
        return "task"
    elif name == "Create page posts in facebook pages":
        return ""
    elif "twitter" in name or "tweet" in name:
        return "create_twitter"
    elif "upload" in name:
        return "upload_to_google_drive"
    elif "slide" in name or "presentation" in name:
        return "create_google_slides"
    elif "reminder" in name:
        return "set_reminder"
    elif "slack" in name:
        return "send_slack_message"
    elif "workday" in name:
        return "workday_pto"
    elif "auto response" in name:
        return "gmail_auto_response"
    elif "github" in name:
        return "create_github_issue"
    else:
        return None
