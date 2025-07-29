from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from schemas.user_schema import UserSchema,LoginSchema, OTPVerificationSchema
from manager.user_manager import UserManager
from utils import generate_access_token, generate_refresh_token, require_standard_headers, decode_token
from models import UserToken
from extensions import db
import logging 
import jwt


user = Blueprint('user', __name__)
user_manager = UserManager()

@user.route('/register', methods=['POST'])
@require_standard_headers
def register():
    """
    Handles user registration.
    """
    try:
        data = UserSchema().load(request.get_json())
        logging.info("Received user registration data")
        user = user_manager.register_user(data)
        if not user:
            logging.warning("Registration failed: User already exists")
            return jsonify({"error": "User already exists"}), 400
        
        logging.info(f"User registration initiated: {data['username']}")
        return jsonify({
            "message": user['message'],
            "user_uid": user['user_uid']
        }), 201
        
    except ValidationError as e:
        logging.error(f"Validation error during registration: {e.messages}")
        return jsonify(e.messages), 400
    except Exception as e:
        logging.error(f"Unexpected error in register: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@user.route('/verify-otp', methods=['POST'])
@require_standard_headers
def verify_otp():
    """
    Verifies OTP and completes user registration.
    """
    try:
        data = OTPVerificationSchema().load(request.get_json())
        logging.info(f"Received OTP verification for user: {data['user_uid']}")
        
        result = user_manager.verify_otp(data['user_uid'], data['otp_code'])
        
        if not result['success']:
            logging.warning(f"OTP verification failed: {result['error']}")
            return jsonify({"error": result['error']}), 400
        
        logging.info(f"OTP verification successful for user: {data['user_uid']}")
        return jsonify({
            "message": result['message'],
            "user": result['user']
        }), 200
        
    except ValidationError as e:
        logging.error(f"Validation error during OTP verification: {e.messages}")
        return jsonify(e.messages), 400
    except Exception as e:
        logging.error(f"Unexpected error in verify_otp: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@user.route('/resend-otp', methods=['POST'])
@require_standard_headers
def resend_otp():
    """
    Resends OTP to user's registered phone number.
    """
    try:
        data = request.get_json()
        user_uid = data.get('user_uid')
        
        if not user_uid:
            return jsonify({"error": "User UID is required"}), 400
        
        logging.info(f"Resending OTP for user: {user_uid}")
        
        result = user_manager.resend_otp(user_uid)
        
        if not result['success']:
            logging.warning(f"OTP resend failed: {result['error']}")
            return jsonify({"error": result['error']}), 400
        
        logging.info(f"OTP resent successfully for user: {user_uid}")
        return jsonify({"message": result['message']}), 200
        
    except Exception as e:
        logging.error(f"Unexpected error in resend_otp: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

@user.route('/login', methods=['POST'])
@require_standard_headers
def login():
    """
    Handles user authentication and generates JWT access and refresh tokens.
    """

    try:
        data = LoginSchema().load(request.get_json())

        user = user_manager.login_user(data['email'], data['password'])
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        access_token, access_expiry = generate_access_token(user.uid)
        refresh_token, refresh_expiry = generate_refresh_token(user.uid)
        device_uuid = request.headers.get("Device-Uuid")

        user_manager.save_token(
            user_uid=user.uid,
            access_token=access_token,
            access_expiry=access_expiry,
            refresh_token=refresh_token,
            refresh_token_expiry=refresh_expiry,
            device_uuid=device_uuid
        )
        
       
        return jsonify({
            "message": f"Welcome {user.first_name}",
            "uid": user.uid,
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        logging.error(f"Error in login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

@user.route('/refresh', methods=['POST'])
@require_standard_headers
def refresh_token_route():
    """
    Generates a new JWT access token using a valid refresh token.
    """

    token = None
    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
        if bearer.startswith("Bearer "):
            token = bearer.split(" ")[1]

    if not token:
        return jsonify({"error": "Refresh token is missing"}), 401

    try:
        # Decode refresh token
        data = decode_token(token)
        user_uid = data["uid"]
        
        # Check if this token exists in DB
        token_record = UserToken.query.filter_by(refresh_token=token, user_uid=user_uid).first()
        if not token_record:
            return jsonify({"error": "Invalid refresh token"}), 401
        
      # Get device_uuid from headers
        incoming_device_uuid = request.headers.get("Device-Uuid")
        if token_record.device_uuid != incoming_device_uuid:
            return jsonify({"error": "Device UUID mismatch"}), 401

        # Generate new access token
        new_access_token, new_access_expiry = generate_access_token(user_uid)

        # Update DB
        token_record.access_token = new_access_token
        token_record.access_token_expiry = new_access_expiry
        db.session.commit()

        return jsonify({"access_token": new_access_token})

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401
    except Exception as e:
        logging.error(f"Error in refresh_token: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

