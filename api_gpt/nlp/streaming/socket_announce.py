from datetime import datetime
import engineio
from api_gpt.utils import get_key_or_default, get_key_or_none
from threading import Lock
from flask import (
    Flask,
    render_template,
    session,
    request,
    copy_current_request_context,
    request,
)
from flask_socketio import (
    SocketIO,
    emit,
    join_room,
    leave_room,
    close_room,
    rooms,
    disconnect,
)
from flask_cors import CORS

socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")

socket_sid_to_user_id = {}
user_id_to_status = {}

thread = None
thread_lock = Lock()


def publish_data_to_socket(data, user):
    try:
        socketio.emit("streaming_data", data, to=user)
    except Exception as exception:
        print("Error in publish streaming data : ", exception, flush=True)


@socketio.on("listen_update")
def listen_update(data):
    userid = data["userid"]
    print("######## listen update : ", userid, flush=True)
    # sid = request.sid
    # socket_sid_to_user_id[sid] = userid
    join_room(userid)


@socketio.event
def join(message):
    print("### join ", flush=True)
    join_room(message["userid"])


@socketio.event
def leave(message):
    print("### leave ", flush=True)
    leave_room(message["userid"])


@socketio.event
def my_ping():
    print("my_pong", flush=True)
    emit("my_pong")


@socketio.on("disconnect")
def disconnect():
    socket_sid = request.sid
    print("### disconnect ", flush=True)
    pass


@socketio.event
def connect():
    print("### connect ", flush=True)
    pass
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(background_thread)
