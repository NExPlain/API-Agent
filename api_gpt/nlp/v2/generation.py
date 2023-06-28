from resttest import app
from flask import request
from modules.utils import *
from api_gpt.nlp.v2.prompt_templates import *
from api_gpt.services.openai_request import *


def generate_ai_generation_v2(
    user_name: str,
    user_id: str,
    email: str,
    current_time: str,
    skills_str: str,
    model: str,
    text: str,
    max_tokens: int,
):
    """Genearete ai generation using v2 logic"""

    system_prompt = generation_prompt_template_v2.format(
        user_name=user_name,
        user_id=user_id,
        email=email,
        current_time=current_time,
        skills_str=skills_str,
    )
    user_prompt = generation_text_template_v2.format(text=text)

    json_response = {"message": "failed"}
    if model == "gpt-3.5-turbo":
        json_response = get_chat_gpt_response(max_tokens, system_prompt, user_prompt)
    else:
        json_response = get_gpt3_generation_result(
            model, max_tokens, system_prompt, user_prompt
        )
    return json_response
