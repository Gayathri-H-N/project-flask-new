import jwt
import random
import logging 
from datetime import datetime, timedelta, timezone
from flask import current_app, request, jsonify
from functools import wraps
from twilio.base.exceptions import TwilioRestException
from twilio_client import get_twilio_client
from twilio_client import twilio_client

def generate_access_token(user_uid): 
    """
    Generates a JWT access token for the given user.
    """
    expires_in = current_app.config.get("ACCESS_TOKEN_EXPIRES", 120)
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "uid": user_uid,
        "type": "access",
        "exp": expiry
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token,expiry

def generate_refresh_token(user_uid): 
    """
    Generates a JWT refresh token for the given user.
    """
    expires_in = current_app.config.get("REFRESH_TOKEN_EXPIRES", 604800)
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "uid": user_uid,
        "type": "refresh",
        "exp": expiry
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token, expiry

def decode_token(token):
    """
    Decodes the given JWT token using the application's secret key.
    """
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def require_standard_headers(f):
    """
    Decorator to ensure required headers are present in the request.
    Checks for 'Content-Type: application/json', 'Device-Name', and 'Device-Uuid' headers.
    """
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
        phone = client.lookups.v2.phone_numbers(phone_number).fetch()
        return {
            "valid": True,
            "number": phone.phone_number,
            "country_code": phone.country_code,
        }
    except TwilioRestException as e:
        return None


def generate_otp():
    """
    Generate a 6-digit OTP.
    """
    return str(random.randint(100000, 999999))


def send_otp_sms(phone_number, otp_code):
    """
    Send OTP via SMS using Twilio.
    """
    try:
        message = twilio_client.messages.create(
            body=f"Your verification code is: {otp_code}. This code will expire in 5 minutes.",
            from_=current_app.config.get('TWILIO_PHONE_NUMBER'),  
            to=phone_number
        )
        logging.info(f"OTP sent successfully to {phone_number}. Message SID: {message.sid}")
        return {
            "success": True,
            "message_sid": message.sid
        }
    except Exception as e:
        logging.error(f"Failed to send OTP to {phone_number}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    

def send_welcome_sms(phone_number, first_name):
    """
    Send welcome SMS after successful registration.
    """
    from twilio_client import twilio_client
    try:
        message = twilio_client.messages.create(
            body=f"Welcome {first_name}! Your account has been successfully created. Thank you for joining us!",
            from_=current_app.config.get('TWILIO_PHONE_NUMBER'),
            to=phone_number
        )
        logging.info(f"Welcome SMS sent successfully to {phone_number}. Message SID: {message.sid}")
        return {
            "success": True,
            "message_sid": message.sid
        }
    except Exception as e:
        logging.error(f"Failed to send welcome SMS to {phone_number}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }