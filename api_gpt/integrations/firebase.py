import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials

# Load environment variables from .env file
load_dotenv()

if "FIREBASE_DATABASE_URL" in os.environ:
    FIREBASE_DATABASE_URL = os.environ["FIREBASE_DATABASE_URL"]
else:
    FIREBASE_DATABASE_URL = None


def init_firebase(testing_environment: bool = False):
    if testing_environment:
        return
    if not firebase_admin._apps:
        # Firebase configuration
        SERVICE_ACCOUNT_FILE = "firebase_service.json"

        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        if FIREBASE_DATABASE_URL:
            firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
        else:
            firebase_admin.initialize_app(cred)
