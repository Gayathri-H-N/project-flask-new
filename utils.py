import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app, request, jsonify
from functools import wraps

def generate_access_token(user_uid, expires_in=120): #2 mins
    payload = {
        "uid": user_uid,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token

def generate_refresh_token(user_uid, expires_in=604800):  # 7 days
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "uid": user_uid,
        "type": "refresh",
        "exp": expiry
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token, expiry

def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def require_standard_headers(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        content_type = request.headers.get("Content-Type")
        device_name = request.headers.get("Device-Name")
        device_uuid = request.headers.get("Device-Uuid")

        if content_type != "application/json":
            return jsonify({"error": "Content-Type must be application/json"}), 400

        if not device_name:
            return jsonify({"error": "Device-Name header is required"}), 400

        if not device_uuid:
            return jsonify({"error": "Device-Uuid header is required"}), 400

        return f(*args, **kwargs)
    return decorated
