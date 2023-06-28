import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData
from api_gpt.workflows.execute.parse_params import parse_value_from_intent

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_email_gmail_api(intent_data: IntentData):
    """Example input:
    to     :    lizhenpi@gmail.com
    subject:    Reminder: Tomorrow's Meeting
    body   :
    Dear Liz, Just a friendly reminder that we have a meeting scheduled for tomorrow. Please make sure to prepare any necessary materials and be ready to discuss the agenda. Looking forward to seeing you there!
    Args:
        intent_data (IntentData): _description_
    """

    email_to = parse_value_from_intent(
        keys=["to", "recei", "recip"], intent_data=intent_data
    )
    email_subject = parse_value_from_intent(
        keys=["subject", "title"], intent_data=intent_data
    )
    email_body = parse_value_from_intent(
        keys=["body", "content"], intent_data=intent_data
    )
    send_email(subject=email_subject, body=email_body, recipient=email_to)


def send_email(subject, body, recipient):
    # Authenticate and authorize Google Gmail API
    creds = None
    try:
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

    # Create a service object for the Google Gmail API
    service = build("gmail", "v1", credentials=creds)

    # Create an email message
    message = create_message(subject, body, recipient)

    # Send the email
    send_message(service, "me", message)


def create_message(subject, body, recipient) -> dict:
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["To"] = recipient
    # Encode the message as a base64 string
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Create the request body
    create_message = {"raw": encoded_message}
    return create_message


def send_message(service, user_id: str, message: dict):
    message = service.users().messages().send(userId=user_id, body=message).execute()
