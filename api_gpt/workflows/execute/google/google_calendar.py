from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import pytz

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.workflows.execute.parse_params import parse_value_from_intent


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def book_meeting_using_google_calendar(intent_data: IntentData):
    """Example input:
    summary   :    Meeting with Zhen Li
    start time:    {current_time}
    end time  :    {current_time + 1 hour}
    attendees :    zhen.li@plasma-ai.com

    Args:
        intent_data (IntentData): _description_
    """
    # Get the meeting details

    meeting_participants = parse_value_from_intent(
        keys=["participant", "attendee"], intent_data=intent_data
    )
    meeting_start_time = parse_value_from_intent(
        keys=["start time", "start"], intent_data=intent_data
    )
    meeting_end_time = parse_value_from_intent(
        keys=["end time", "end"], intent_data=intent_data
    )
    meeting_title = parse_value_from_intent(
        keys=[
            "title",
            "summary",
        ],
        intent_data=intent_data,
    )
    meeting_agenda = parse_value_from_intent(
        keys=["agenda", "content", "summary", "title"], intent_data=intent_data
    )

    try:
        # Authenticate and authorize Google Calendar API
        creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080)
    except Exception as e:
        raise ValueError(
            f"Missing firebase credentials to execute, please refer to https://developers.google.com/workspace/guides/create-credentials, error log: {str(e)}"
        )

    # Create a service object for the Google Calendar API
    service = build("calendar", "v3", credentials=creds)

    print(f"meeting_start_time : {meeting_start_time}")

    # Create an event object for the meeting
    event = {
        "summary": meeting_title,
        "start": {
            "dateTime": meeting_start_time,
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": meeting_end_time,
            "timeZone": "UTC",
        },
        "description": meeting_agenda,
        "attendees": [
            {"email": email.strip()} for email in meeting_participants.split(",")
        ],
    }

    # Call the Google Calendar API to insert the event
    event = service.events().insert(calendarId="primary", body=event).execute()
