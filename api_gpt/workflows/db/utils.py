from time import time
from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.data_structures.proto.generated.intent_input_pb2 import IntentInput
from api_gpt.data_structures.proto.generated.intent_output_pb2 import IntentOutput
from api_gpt.data_structures.proto.generated.intent_template_pb2 import IntentTemplate


def convert_to_intent_template(intent_data: IntentData):
    intent_template = IntentTemplate()
    intent_template.app_name = intent_data.app_name
    intent_template.name = intent_data.name
    intent_template.meta_data.MergeFrom(intent_data.meta_data)
    intent_template.execute_endpoint = intent_data.api_url
    for input in intent_data.inputs:
        add_input = IntentInput()
        add_input.MergeFrom(input)
        add_input.parameter.value = ""
        intent_template.inputs.append(add_input)
    for output in intent_data.outputs:
        add_output = IntentOutput()
        add_output.MergeFrom(output)
        add_output.parameter.value = ""
        intent_template.outputs.append(add_output)
    intent_template.create_timestamp = str(int(time()))

    return intent_template
