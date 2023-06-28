from api_gpt.nlp.streaming.streaming_multi_step import (
    generate_quick_workflow_multi_step,
    perform_request_with_streaming_multi_step,
)
from api_gpt.nlp.streaming.streaming_simple import (
    generate_quick_workflow,
    perform_request_with_streaming,
)
from api_gpt.utils import token_required
from google.protobuf.json_format import MessageToJson

from api_gpt.utils import *
from timeit import default_timer as timer


@current_app.route("/workflow/generate_simple", methods=["POST"])
@token_required
def workflow_generate_simple():
    try:
        _json = request.json
        text = get_key_or_none(_json, "text")
        workflow_id = get_key_or_default(_json, "workflow_id", "")
        workflow_data = generate_quick_workflow_multi_step(text, workflow_id)
        return json.loads(MessageToJson(workflow_data))

    except Exception as e:
        return "Failed with : " + str(e), 500


@current_app.route("/workflow/generate_streaming", methods=["POST"])
@token_required
def workflow_generate_streaming():
    try:
        _json = request.json
        text = get_key_or_none(_json, "text")
        user = get_key_or_none(_json, "user")
        max_tokens = get_key_or_default(_json, "max_tokens", 500)
        workflow_id = get_key_or_default(_json, "workflow_id", "")
        start = timer()
        workflow_data, openai_response = perform_request_with_streaming(
            text, user, workflow_id, max_tokens
        )
        end = timer()
        if workflow_data != None:
            return workflow_data
        else:
            return openai_response

    except Exception as e:
        return "Failed with : " + str(e), 500


@current_app.route("/workflow/generate_streaming_multi", methods=["POST"])
@token_required
def workflow_generate_streaming_multi():
    try:
        _json = request.json
        text = get_key_or_none(_json, "text")
        user = get_key_or_none(_json, "user")
        max_tokens = get_key_or_default(_json, "max_tokens", 500)
        workflow_id = get_key_or_default(_json, "workflow_id", "")
        start = timer()
        workflow_data, openai_response = perform_request_with_streaming_multi_step(
            text, user, workflow_id, max_tokens
        )
        end = timer()
        if workflow_data != None:
            return workflow_data
        else:
            return openai_response

    except Exception as e:
        return "Failed with : " + str(e), 500
