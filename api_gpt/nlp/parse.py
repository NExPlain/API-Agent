from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData


def convert_json_response_to_workflow(workflow_dict) -> WorkflowData:
    workflow_data = WorkflowData()
    workflow_data.name = workflow_dict["workflow"]
    for skill_data in workflow_dict["skills"]:
        intent_data = workflow_data.intent_data.add()
        intent_data.name = skill_data["skill_name"]
        # TODO: parse the intent type

        for parameter in skill_data["parameters"]:
            # TODO parse the parameter type
            input = intent_data.inputs.add()
            input.parameter.name = parameter["name"]
            input.parameter.value = parameter["value"]

        for return_val in skill_data["returns"]:
            # TODO parse the parameter type
            output = intent_data.outputs.add()
            output.parameter.name = return_val["name"]
            output.parameter.value = return_val["value"]

    return workflow_data
