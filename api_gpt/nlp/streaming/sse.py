from flask import Response
from configdb import mysql
from configdb import mySQLConnectionPool
import pymysql
from flask_sse import sse
from flask import current_app
import time


def get_message():
    """this could be any function that blocks until data is ready"""
    time.sleep(1.0)
    s = time.ctime(time.time())
    return s


@current_current_app.route("/stream")
def stream():
    def eventStream():
        print("data!")
        # wait for source data to be available, then push it
        yield "data: {}\n\n".format(get_message())

    print("stream", flush=True)
    return Response(eventStream(), mimetype="text/event-stream")
