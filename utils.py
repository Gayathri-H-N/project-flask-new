import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app, request, jsonify
from functools import wraps
from twilio.base.exceptions import TwilioRestException
from twilio_client import get_twilio_client

def generate_access_token(user_uid, expires_in=120): #2 mins
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "uid": user_uid,
        "type": "access",
        "exp": expiry
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token,expiry

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


def validate_phone_number(phone_number):
    """
    Validates a phone number using Twilio Lookup API.
    Returns a dict with details if valid, else None.
    """
    try:
        client = get_twilio_client()
        phone = client.lookups.v2.phone_numbers(phone_number).fetch(type=["carrier"])
        return {
            "valid": True,
            "number": phone.phone_number,
            "country_code": phone.country_code,
            "carrier": phone.carrier
        }
    except TwilioRestException as e:
        return None
