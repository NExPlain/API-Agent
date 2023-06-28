from api_gpt.services.openai_request import get_openai_response_string
from api_gpt.settings.debug import global_debug_flag

CLASSIFY_TASK_PROMPT = ""

with open("api_gpt/nlp/prompts/classify_task_prompt.txt") as f:
    CLASSIFY_TASK_PROMPT = f.read()


def is_single_task(text, model, max_tokens) -> False:
    system_prompt = CLASSIFY_TASK_PROMPT
    user_prompt = f"Text: {text}"
    string_repsonse = get_openai_response_string(
        model, max_tokens, system_prompt, user_prompt
    )
    if global_debug_flag:
        print("Classification results : ", string_repsonse, flush=True)
    if "simple" in string_repsonse.lower():
        return True
    else:
        return False
