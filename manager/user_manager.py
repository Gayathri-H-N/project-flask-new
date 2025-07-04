import logging
from extensions import bcrypt
from models import User
from sql_files.user_sql import (
    get_user_by_email,
    get_user_by_username,
    insert_user,
    insert_user_token,
    is_email_registered,
    is_username_taken,
    is_mobile_registered
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
            if is_mobile_registered(data['mobile_number']):
                logging.warning(f"Registration failed: Mobile number already exists - {data['mobile_number']}")
                return None

            hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user = User(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                mobile_number=data['mobile_number'],
                password=hashed_pw
            )

            logging.info(f"Registering new user: {user.username}")
            return insert_user(user)

        except KeyError as e:
            logging.warning(f"Missing registration field: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in register_user: {e}")
            return None


     def login_user(self, email, password):
        """
        Authenticates a user by verifying email and password.
        """

        try:
            user = get_user_by_email(email)
            if user and bcrypt.check_password_hash(user.password, password):
                logging.info(f"Login successful for user: {email}")
                return user

            logging.warning(f"Login failed for user: {email}")
            return None

        except Exception as e:
            logging.error(f"Unexpected error in login_user: {e}")
            return None
        

     def save_token(self, user_uid, access_token, refresh_token, refresh_token_expiry=None):
        """
        Saves a user's tokens to the database.
        """
        try:
            return insert_user_token(
                user_uid=user_uid,
                access_token=access_token,
                refresh_token=refresh_token,
                refresh_token_expiry=refresh_token_expiry
            )
        except Exception as e:
            logging.error(f"Error saving tokens for user_uid {user_uid}: {str(e)}")
            return None

   