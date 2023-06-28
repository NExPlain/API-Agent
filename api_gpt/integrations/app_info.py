import os

import requests
from firebase_admin import db
from flask import current_app
from waiting import wait

from api_gpt.data_structures.proto.generated.meta_data_pb2 import MetaData


class AppInfoHandler:
    _instance = None
    _testing_environment = False

    @classmethod
    def initInstance(
        cls, GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX, testing_environment: bool = False
    ):
        if cls._instance is None:
            cls._testing_environment = testing_environment
            cls._instance = cls(
                GOOGLE_SEARCH_KEY,
                GOOGLE_SEARCH_CX,
                init_with_data=not testing_environment,
            )

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            raise ValueError("AppInfoHandler instance is not initialized")
        return cls._instance

    def __init__(
        self, GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX, init_with_data: bool = False
    ):
        self.app_logo_ref_location = "plasma/app_info/logos"
        self.is_app_logo_init = False
        self.app_logos = {}
        self.GOOGLE_SEARCH_KEY = GOOGLE_SEARCH_KEY
        self.GOOGLE_SEARCH_CX = GOOGLE_SEARCH_CX
        if init_with_data:
            self.app_logos_ref = db.reference(self.app_logo_ref_location)
            self.init_app_logos_from_database()
            self.app_logos_ref.listen(self.app_logos_listener)

    def app_logos_listener(self, event):
        if event is None:
            return
        try:
            if event.event_type == "put":
                if event.data is None:
                    return
                event_path = event.path
                if event.path == "/" and event.data is not None:
                    self.app_logos = event.data
                if event_path.count("/") == 1:
                    key = event_path[1:]
                    self.app_logos[key] = event.data
                if event_path.count("/") == 2:
                    _, key, value = event_path.split("/")
                    if key not in self.app_logos:
                        self.app_logos[key] = {}
                    self.app_logos[key][value] = event.data
        except Exception as exception:
            pass

    def write_app_logo(
        self, app_name_key: str, app_type: str, app_name: str, url: str, thumbnail: str
    ):
        data = {"type": app_type, "name": app_name, "url": url, "thumbnail": thumbnail}
        self.app_logos[app_name_key] = data
        messages_ref = db.reference(f"{self.app_logo_ref_location}/{app_name_key}")
        if not messages_ref.get():
            print("write logo ", app_name_key, flush=True)
            messages_ref.set(data)

    def init_app_logos_from_database(self):
        messages = self.app_logos_ref.get()
        if messages:
            self.app_logos = messages
        else:
            self.app_logos = {}
        self.is_app_logo_init = True

    def search_app_logo(self, app_name: str):
        if not self.GOOGLE_SEARCH_KEY or not self.GOOGLE_SEARCH_CX:
            return None, None
        try:
            r = requests.get(
                f"https://www.googleapis.com/customsearch/v1?key={self.GOOGLE_SEARCH_KEY}&cx={self.GOOGLE_SEARCH_CX}&q={app_name} logo&searchType=image"
            )
            items = r.json()["items"]
            for item in items:
                try:
                    link = item["link"]
                    image = item["image"]
                    thumbnail = image["thumbnailLink"]
                    return link, thumbnail
                except Exception as exception:
                    continue
        except Exception as exception:
            return None, None

    @staticmethod
    def get_app_key_from_name(app_name: str) -> str:
        return app_name.lower().replace(" ", "_").replace(".", "_")

    def get_app_logo_url(self, type: str, app_name: str):
        if app_name.lower() == "gmail":
            return (
                "https://imagedelivery.net/jibXaOdYD8DNFxnmU6ibvw/2d344a9e-8dd9-424c-2c85-74f3084c4800/public",
                "https://imagedelivery.net/jibXaOdYD8DNFxnmU6ibvw/2d344a9e-8dd9-424c-2c85-74f3084c4800/public",
            )
        elif app_name.lower() == "google calendar":
            return (
                "https://imagedelivery.net/jibXaOdYD8DNFxnmU6ibvw/4a6337ae-cf1b-4779-0baa-8f6f60dbba00/public",
                "https://imagedelivery.net/jibXaOdYD8DNFxnmU6ibvw/4a6337ae-cf1b-4779-0baa-8f6f60dbba00/public",
            )
        if self._testing_environment:
            return "", ""
        wait(
            lambda: (self.is_app_logo_init),
            timeout_seconds=120,
            waiting_for="Waiting for app_logos be init",
        )
        app_name_key = self.get_app_key_from_name(app_name)
        if app_name_key in self.app_logos and "url" in self.app_logos[app_name_key]:
            url = self.app_logos[app_name_key]["url"]
            thumbnail = self.app_logos[app_name_key]["thumbnail"]
            return url, thumbnail
        failed_count = 0
        if app_name_key in self.app_logos:
            failed_count = self.get_key_or_default(
                self.app_logos[app_name_key], "count", 0
            )
        if failed_count >= 5:
            return "", ""
        url, thumbnail_url = self.search_app_logo(app_name)
        self.write_app_logo(app_name_key, type, app_name, url, thumbnail_url)
        return url, thumbnail_url

    def get_meta_data(self, type: str, app_name: str) -> MetaData:
        meta_data = MetaData()
        if len(app_name) >= 100:
            return meta_data
        if app_name == "Plasma":
            if "task" in type.lower():
                meta_data.emoji = "📃"
                return meta_data
            elif "reminder" in type.lower():
                meta_data.emoji = "🔔"
                return meta_data
        logo_url, thumbnail = self.get_app_logo_url(type, app_name)
        meta_data.logo_url = logo_url
        meta_data.thumbnail = thumbnail
        return meta_data


def init_app_info_handler(testing_environment: bool = False):
    if "GOOGLE_SEARCH_KEY" in os.environ:
        GOOGLE_SEARCH_KEY = os.environ["GOOGLE_SEARCH_KEY"]
    else:
        GOOGLE_SEARCH_KEY = None

    if "GOOGLE_SEARCH_CX" in os.environ:
        GOOGLE_SEARCH_CX = os.environ["GOOGLE_SEARCH_CX"]
    else:
        GOOGLE_SEARCH_CX = None

    AppInfoHandler.initInstance(
        GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX, testing_environment=testing_environment
    )
