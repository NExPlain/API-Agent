import logging
from dotenv import load_dotenv
from dynaconf import FlaskDynaconf
from flask import Flask
import logging
import sys
from api_gpt.integrations.app_info import init_app_info_handler
from api_gpt.integrations.firebase import init_firebase
import os
from api_gpt.workflows.db.apps_template import init_app_template_handler

from api_gpt.workflows.db.intent_template import init_intent_templates_handler
from api_gpt.workflows.db.workflow_template import init_workflow_template_handler


def init_firebase_handlers(testing_environment: bool = False):
    print("start init_firebase_handlers")
    init_firebase(testing_environment)
    init_app_info_handler(testing_environment)
    init_intent_templates_handler(testing_environment)
    init_workflow_template_handler(testing_environment)
    init_app_template_handler(testing_environment)
    print("init_firebase_handlers done")


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app)  # config managed by Dynaconf
    app.config.load_extensions("EXTENSIONS")  # Load extensions from settings.toml
    app.config.update(config)  # Override with passed config
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # Load environment variables from .env file
    load_dotenv()
    init_firebase_handlers()
    return app


def create_app_wsgi():
    # workaround for Flask issue
    # that doesn't allow **config
    # to be passed to create_app
    # https://github.com/pallets/flask/issues/4170
    app = create_app()
    return app
