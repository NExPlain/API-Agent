import json

from firebase_admin import credentials, db
from google.protobuf.json_format import MessageToJson

from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData
from api_gpt.integrations.firebase import init_firebase
from api_gpt.settings.debug import global_debug_flag


## When requested, write the workflow into two spaces.
def write_debrief_workflow(
    user_id: str, message_id: str, action_name: str, workflow: WorkflowData
):
    try:
        if global_debug_flag:
            print("writing debrief workflow : ", workflow.id, workflow)
        # Write the workflow
        if not workflow.id:
            return
        workflow_json = json.loads(MessageToJson(workflow))
        messages_ref = db.reference(f"debrief/workflows/{user_id}/{workflow.id}")
        messages_ref.set(workflow_json)

        # debrief workflow
        debrief_ref = db.reference(
            f"debrief/message_to_workflow/{user_id}/{message_id}"
        )
        cur_debrief_workflow = debrief_ref.get()
        action_to_workflow_id = {}
        if cur_debrief_workflow and "actionToWorkflowId" in cur_debrief_workflow:
            action_to_workflow_id = cur_debrief_workflow["actionToWorkflowId"]
        action_to_workflow_id[action_name] = workflow.id
        cur_debrief_workflow = {
            "messageId": message_id,
            "actionToWorkflowId": action_to_workflow_id,
        }
        debrief_ref.set(cur_debrief_workflow)

        if global_debug_flag:
            print("finished writing debrief workflow")
    except Exception as e:
        print("Error in write_debrief_workflow : ", e, flush=True)
