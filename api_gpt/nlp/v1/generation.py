from typing import Optional
from flask import request
from api_gpt.utils import *

from api_gpt.nlp.v1.prompt_templates import *
from api_gpt.nlp.v2.prompt_templates import *
from api_gpt.services.openai_request import *


def fetch_generate_v1_response(
    user_name: str,
    user_id: str,
    email: str,
    current_time: str,
    participants_string: str,
    text: str,
    max_tokens: int,
    model: str,
) -> Optional[map]:
    system_prompt = generation_prompt_template_v2.format(
        current_time=current_time, skills_str=""
    )
    user_prompt = generation_text_template.format(text=text)

    json_response = {"message": "failed"}
    if model == "gpt-3.5-turbo":
        json_response = get_chat_gpt_response(max_tokens, system_prompt, user_prompt)
    else:
        json_response = get_gpt3_generation_result(
            model, max_tokens, system_prompt, user_prompt
        )
    return json_response


def fetch_generate_v1_string(
    user_name: str,
    user_id: str,
    email: str,
    current_time: str,
    participants_string: str,
    text: str,
    max_tokens: int,
    model: str,
) -> Optional[str]:
    try:
        json_response = fetch_generate_v1_response(
            user_name,
            user_id,
            email,
            current_time,
            participants_string,
            text,
            max_tokens,
            model,
        )
        if json_response == None:
            return None

        if model == "gpt-3.5-turbo":
            response = json_response["choices"][0]["message"]["content"]
        else:
            response = json_response["choices"][0]["text"]
        return response
    except Exception as e:
        return None
