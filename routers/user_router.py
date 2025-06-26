from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from schemas.user_schema import UserSchema,LoginSchema
from manager.user_manager import UserManager
import logging  

user = Blueprint('user', __name__)
user_manager = UserManager()

@user.route('/register', methods=['POST'])
def register():
    try:
        data = UserSchema().load(request.get_json())
        logging.info("Received user registration data")
        user = user_manager.register_user(data)
        if not user:
            logging.warning("Registration failed: User already exists")
            return jsonify({"error": "User already exists"}), 400
        logging.info(f"User registered successfully: {user.username}")
        return jsonify({"message": "User registered", "uid": user.uid}), 201
    except ValidationError as e:
        logging.error(f"Validation error during registration: {e.messages}")
        return jsonify(e.messages), 400

@user.route('/login', methods=['POST'])
def login():
    try:
        data = LoginSchema().load(request.get_json())
        logging.info(f"Login attempt for email: {data['email']}")
        user = user_manager.login_user(data['email'], data['password'])
        if not user:
            logging.warning("Login failed: Invalid credentials")
            return jsonify({"error": "Invalid credentials"}), 401
        logging.info(f"User logged in successfully: {user.username}")
        return jsonify({"message": f"Welcome {user.first_name}", "uid": user.uid})
    except ValidationError as e:
        logging.error(f"Validation error during login: {e.messages}")
        return jsonify(e.messages), 400
