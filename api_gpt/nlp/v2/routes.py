from api_gpt.utils import *
from api_gpt.nlp.v2.generation import *
from flask import current_app


@current_app.route("/plasma_ai_generation_v2", methods=["POST"])
@token_required
def plasma_ai_generation_v2():
    try:
        _json = request.json
        loginemail = _json["loginemail"]
        model = _json["model"]
        user_name = get_key_or_none(_json, "user_name")
        user_id = get_key_or_none(_json, "user_id")
        email = get_key_or_none(_json, "email")
        current_time = get_key_or_none(_json, "current_time")
        skills_str = get_key_or_none(_json, "skills_str")
        participants_string = get_key_or_none(_json, "participants_string")
        max_tokens = get_key_or_default(_json, "max_tokens", 128)
        text = get_key_or_none(_json, "text")
        json_response = generate_ai_generation_v2(
            user_name=user_name,
            user_id=user_id,
            email=email,
            current_time=current_time,
            skills_str=skills_str,
            max_tokens=max_tokens,
            text=text,
            model=model,
        )
        return {"message": "success", "status_code": 200, "data": json_response}

    except Exception as e:
        print("Error in plasma_ai_generation ", e, flush=True)
