import datetime
import time
from typing import Tuple

from google.protobuf.json_format import Parse, ParseDict

from api_gpt.data_structures.proto.generated.execution_data_pb2 import ExecutionData
from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.workflows.execute.google.gmail import send_email_gmail_api
from api_gpt.workflows.execute.google.google_calendar import (
    book_meeting_using_google_calendar,
)


def fill_execution_result_display(
    intent_data: IntentData, execution_data: ExecutionData
):
    app_name = intent_data.app_name
    if app_name.lower() == "gmail":
        execution_data.result.display_link = "https://mail.google.com/mail/u/0/"
        execution_data.result.display_name = "View in gmail"
        return
    elif app_name.lower() == "google calendar":
        execution_data.result.display_link = (
            "https://calendar.google.com/calendar/u/0/r"
        )
        execution_data.result.display_name = "View in Calendar"
        return

    execution_data.result.display_link = ""
    execution_data.result.display_name = "Done"


async def execute_intent(intent_data: IntentData) -> ExecutionData:
    """
    Executes an intent and returns the execution data.

    Args:
        intent_data (IntentData): The data associated with the intent.

    Returns:
        ExecutionData: The execution data containing the result of the intent execution.
    """

    execution_data = ExecutionData()
    execution_data.execution_time = int(round(datetime.datetime.now().timestamp()))
    execution_data.executor_id = "API GPT demo"
    execution_result = execution_data.result
    try:
        is_success = True
        if (
            "google" in intent_data.app_name.lower()
            and "calendar" in intent_data.app_name.lower()
        ):
            book_meeting_using_google_calendar(intent_data)
        elif "gmail" in intent_data.app_name.lower():
            send_email_gmail_api(intent_data)
        else:
            is_success = False
        if is_success:
            execution_result.error_code = 200
            execution_result.is_success = True
            fill_execution_result_display(
                intent_data=intent_data, execution_data=execution_data
            )
        else:
            execution_result.error_code = 204
            execution_result.is_success = True
            execution_data.result.display_link = ""
            execution_data.result.display_name = f"Integrate {intent_data.app_name}"

    except Exception as e:
        execution_result.error_code = 500
        execution_result.is_success = False
        execution_result.error_message = str(e)

    return execution_data
