from flask import current_app

from api_gpt.services.constants import CHATGPT_MODEL, DEFAULT_MAX_TOKENS
from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.workflows.notification_context import NotificationContext

GENERATE_DEBRIEF_ACTIONS_SYSTEM_PROMPT = ""
with open("api_gpt/nlp/debrief/prompts/generate_action_system_prompts.txt") as f1:
    try:
        GENERATE_DEBRIEF_ACTIONS_SYSTEM_PROMPT = f1.read()
    except Exception as e:
        current_app.logger.debug("failed in reading enerate_action_system_prompts", e)


def generate_action_dict(context: NotificationContext) -> dict:
    default_actions_dict = {
        "Reply positively": "Reply positively",
        "Reply negatively": "Reply negatively",
    }
    system_prompt = GENERATE_DEBRIEF_ACTIONS_SYSTEM_PROMPT
    snippet = context.email_dict["content"]
    if len(snippet) >= 2000:
        snippet = snippet[:2000]
    debrief_context = context.context.replace("\n", " ")
    user_prompt = f"Context: {debrief_context}\nSubject: {context.email_dict['subject']}\nFrom: {context.email_dict['from']}\nContent: {snippet}\nActions: "

    response = get_openai_response_string(
        CHATGPT_MODEL, 100, system_prompt, user_prompt
    )
    # current_app.logger.debug('#### user_prompt : ', user_prompt)
    # current_app.logger.debug('#### response : ', response)
    if response is None or ("ignore" in response.lower() and len(response) <= 10):
        return default_actions_dict
    ret = {}
    for action in response.split("|"):
        action = action.replace(".", "").strip()
        # $ # [ ] /
        # action = action.replace('#', '')
        # action = action.replace('$', '')
        # action = action.replace('[', '')
        # action = action.replace(']', '')
        action = action.replace("/", "")
        action = action.strip()
        if (
            action.lower() == "none"
            or action.lower() == "ignore"
            or action.lower().startswith("ignore")
        ):
            continue
        ret[action] = action
    # current_app.logger.debug(f'ret : {ret}, len(ret): {len(ret)}')
    if len(ret) == 0:
        return default_actions_dict
    return ret
