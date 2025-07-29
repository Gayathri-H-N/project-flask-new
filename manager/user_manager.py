#user_manager.py
import logging
from extensions import bcrypt
from models import User
from flask import current_app
from utils import validate_phone_number, generate_otp, send_otp_sms, send_welcome_sms
from sql_files.user_sql import (
    get_user_by_email,
    get_user_by_username,
    get_user_by_uid,
    insert_user,
    insert_user_token,
    is_email_registered,
    is_username_taken,
    # is_mobile_registered,
    update_user_phone_verification
)
from sql_files.otp_sql import (
    store_otp,
    get_latest_valid_otp,
    mark_otp_as_used,
    count_otp_requests_recent,
    get_latest_unexpired_unused_otp,
)


class UserManager:
     def register_user(self, data):
        """
        Registers a new user after checking for duplicate email, username, or mobile number.
        """

        try:
            if is_email_registered(data['email']):
                logging.warning(f"Registration failed: Email already exists - {data['email']}")
                return None
            if is_username_taken(data['username']):
                logging.warning(f"Registration failed: Username already exists - {data['username']}")
                return None
            # if is_mobile_registered(data['mobile_number']):
            #     logging.warning(f"Registration failed: Mobile number already exists - {data['mobile_number']}")
            #     return None
            
            phone = data['mobile_number']
            validation_result = validate_phone_number(phone)
            if not validation_result:
                logging.warning(f"Registration failed: Invalid phone number - {phone}")
                return None

            pepper = current_app.config["PEPPER"]
            password_with_pepper = data['password'] + pepper
            hashed_pw = bcrypt.generate_password_hash(password_with_pepper).decode('utf-8')

            user = User(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                mobile_number=validation_result['number'],
                password=hashed_pw
            )

            # logging.info(f"Registering new user: {user.username}")
            # return insert_user(user)
            created_user = insert_user(user)
            otp_code = generate_otp()
            sms_result = send_otp_sms(validation_result['number'], otp_code)
            if not sms_result['success']:
                logging.error(f"Failed to send OTP to {validation_result['number']}")
                return {"success": False, "error": "Failed to send OTP"}

            store_otp(
                user_uid=created_user.uid,
                otp_code=otp_code,
                purpose='phone_verification',
            )

            logging.info(f"User registration initiated for: {user.username}")
            return {
                "success": True,
                "user_uid": created_user.uid,
                "message": "Registration initiated. Please verify your phone number with the OTP sent."
            }

        except KeyError as e:
            logging.warning(f"Missing registration field: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in register_user: {e}")
            return None


     def verify_otp(self, user_uid, otp_code):
        """
        Verifies the OTP and completes user registration.
        """
        try:
            otp_record = get_latest_valid_otp(user_uid, otp_code, 'phone_verification')
            
            if not otp_record:
                logging.warning(f"OTP verification failed for user {user_uid}")
                return {"success": False, "error": "Invalid or expired OTP"}
            
            mark_otp_as_used(otp_record)
            
            user = update_user_phone_verification(user_uid, True)
            
            if not user:
                logging.error(f"Failed to update phone verification for user {user_uid}")
                return {"success": False, "error": "Failed to complete verification"}
            
            send_welcome_sms(user.mobile_number, user.first_name)
            
            logging.info(f"Phone verification completed for user: {user.username}")
            return {
                "success": True,
                "message": "Phone number verified successfully! Registration completed.",
                "user": {
                    "uid": user.uid,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "phone_verified": user.phone_verified
                }
            }
            
        except Exception as e:
            logging.error(f"Unexpected error in verify_otp: {e}")
            return {"success": False, "error": "Internal server error"}
        

     def resend_otp(self, user_uid):
        """
        Resends OTP to user's registered phone number.
        """
        try:
            user = get_user_by_uid(user_uid)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            if user.phone_verified:
                return {"success": False, "error": "Phone number already verified"}
            
            recent_count = count_otp_requests_recent(user_uid, 'phone_verification', interval_minutes=15)
            if recent_count >= 3:
                return {"success": False, "error": "Too many OTP requests. Please try again later."}
            
            latest_otp = get_latest_unexpired_unused_otp(user_uid, 'phone_verification')
            if latest_otp:
            # Resend existing OTP
                sms_result = send_otp_sms(user.mobile_number, latest_otp.otp_code)
                if not sms_result['success']:
                    return {"success": False, "error": "Failed to resend OTP"}
                return {"success": True, "message": "Existing OTP resent successfully"}
            
            otp_code = generate_otp()
            sms_result = send_otp_sms(user.mobile_number, otp_code)  
            if not sms_result['success']:
                return {"success": False, "error": "Failed to send OTP"}
            
            store_otp(
                user_uid=user.uid,
                otp_code=otp_code,
                purpose='phone_verification',
            )
            
            logging.info(f"OTP resent to user: {user.username}")
            return {"success": True, "message": "OTP resent successfully"}
            
        except Exception as e:
            logging.error(f"Unexpected error in resend_otp: {e}")
            return {"success": False, "error": "Internal server error"}


     def login_user(self, email, password):
        """
        Authenticates a user by verifying email and password.
        """

        try:
            user = get_user_by_email(email)
            pepper = current_app.config["PEPPER"]
            password_with_pepper = password + pepper
            if user and bcrypt.check_password_hash(user.password, password_with_pepper):
                logging.info(f"Login successful for user: {email}")
                return user

            logging.warning(f"Login failed for user: {email}")
            return None

        except Exception as e:
            logging.error(f"Unexpected error in login_user: {e}")
            return None
        

     def save_token(self, user_uid, access_token, access_expiry, refresh_token, refresh_token_expiry=None, device_uuid=None):
        """
        Saves a user's tokens to the database.
        """
        try:
            return insert_user_token(
                user_uid=user_uid,
                access_token=access_token,
                access_token_expiry=access_expiry,
                refresh_token=refresh_token,
                refresh_token_expiry=refresh_token_expiry,
                device_uuid=device_uuid
            )
        except Exception as e:
            logging.error(f"Error saving tokens for user_uid {user_uid}: {str(e)}")
            return None

   