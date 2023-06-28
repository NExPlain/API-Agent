import time
import uuid
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.data_structures.proto.generated.workflow_template_pb2 import (
    WorkflowTemplate,
)


def get_workflow_data_from_template(
    workflow_template: WorkflowTemplate,
) -> WorkflowData:
    workflow_data = WorkflowData()
    workflow_data.name = workflow_template.name
    workflow_data.id = str(uuid.uuid4())
    workflow_data.create_timestamp = int(time.time())
    for intent in workflow_template.intents:
        workflow_data.intent_data.append(intent)
    return workflow_data
