from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import jsonify, request
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            raw_token = request.headers["Authorization"]
            if len(raw_token.split(" ")) == 2:
                token = raw_token.split(" ")[1]

        if not token:
            return jsonify({"message": "a valid token is missing"})
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except:
            return jsonify({"message": "token is invalid"})

        return f(*args, **kwargs)

    return decorator


def get_current_timestamp():
    nowtime = datetime.utcnow().replace(tzinfo=timezone.utc)
    now = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    return now


def get_timestamp(dtdt):
    dttime = dtdt.utcnow().replace(tzinfo=timezone.utc)
    dt = dttime.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def jsoncreatetime_tostrtime(x):
    for item in x.keys():
        if type(x[item]) == type(datetime.utcnow()):
            x[item] = x[item].strftime("%Y-%m-%d %H:%M:%S")
    return x


def returnerr(_statuscode, _errmsg):
    response = {}
    response["message"] = _errmsg
    response["status_code"] = _statuscode
    return response


def get_key_or_none(json, key):
    if json == None:
        return None
    if key in json:
        return json[key]
    return None


def get_key_or_default(json, key, default_val):
    if json == None:
        return default_val
    if key in json:
        return json[key]
    return default_val


def close_conn(cursor, conn):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def failed_response(status_code=500, message=""):
    return {"status_code": status_code, "message": message}


def success_response(status_code=200, message=""):
    return {"status_code": status_code, "message": message}
