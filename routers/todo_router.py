import logging
import jwt
from flask import Blueprint, request, jsonify
from schemas.todo_schema import ToDoCreateSchema, ToDoQuerySchema, ToDoResponseSchema, ToDoUpdateSchema
from manager.todo_manager import ToDoManager
from marshmallow import ValidationError
from functools import wraps
from utils import decode_token

todo = Blueprint('todo', __name__)
todo_manager = ToDoManager()

def token_required(f):
    """
    Decorator to validate the JWT access token and inject the current user's UID into the route function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = decode_token(token)
            current_user_uid = data["uid"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_uid, *args, **kwargs)
    return decorated

@todo.route('/create', methods=['POST'])
@token_required
def create_todo(current_user_uid):
    """
    Creates a new ToDo item for the authenticated user.
    """

    try:
        # user_uid = request.args.get('user_uid')
        # if not user_uid:
        #     logging.warning("Create ToDo failed: user_uid missing in query parameters")
        #     return jsonify({'error': 'user_uid is required in query parameters'}), 400

        data = ToDoCreateSchema().load(request.get_json())
        todo_item, error = todo_manager.create(data['task'], data['description'], current_user_uid)
        if error:
            logging.warning(f"Create ToDo failed: {error}")
            return jsonify({"error": error}), 404

        logging.info(f"ToDo created successfully for user_uid {current_user_uid}")
        return jsonify({"message": "ToDo created", "todo_uid": todo_item.uid}), 201
    except ValidationError as e:
        logging.warning(f"Validation error while creating ToDo: {e.messages}")
        return jsonify(e.messages), 400
    except Exception as e:
        logging.error(f"Internal server error in create_todo: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@todo.route('/gettodo', methods=['GET'])
@token_required
def get_todos(current_user_uid):
    """
    Retrieves ToDo items for the authenticated user, optionally filtered by date.
    """

    try:
        # user_uid = request.args.get('user_uid')
        # if not user_uid:
        #     logging.warning("Get ToDos failed: user_uid missing in query parameters")
        #     return jsonify({'error': 'user_uid is required in query parameters'}), 400
            
        logging.info(f"Fetching todos for user_uid: {current_user_uid}")
        params = ToDoQuerySchema().load(request.args)
        date = params.get('date')
        todos, error = todo_manager.get_by_user_uid(current_user_uid, date)
        if error:
            logging.warning(f"Get ToDos failed: {error}")
            return jsonify({"error": error}), 404
        return jsonify(ToDoResponseSchema(many=True).dump(todos))
    except ValidationError as e:
        logging.warning(f"Validation error in get_todos: {e.messages}")
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except Exception as e:
        logging.error(f"Internal server error in get_todos: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@todo.route('/delete', methods=['DELETE'])
@token_required
def delete_todo(current_user_uid):
    """
    Deletes a ToDo item by its UID for the authenticated user.
    """

    try:
        todo_uid = request.args.get('todo_uid')
        if not todo_uid:
            logging.warning("Delete ToDo failed: todo_uid missing in query parameters")
            return jsonify({'error': 'todo_uid is required in query parameters'}), 400

        logging.info(f"Attempting to delete todo with uid: {todo_uid} for user {current_user_uid}")
        success, error = todo_manager.delete_by_uid(todo_uid, current_user_uid)
        if error:
            logging.warning(f"Delete ToDo failed: {error}")
            return jsonify({"error": error}), 404
        
        if success:
            logging.info(f"ToDo with uid {todo_uid} deleted successfully user {current_user_uid}")
            return jsonify({"message": "Todo deleted successfully"}), 200
        else:
            logging.warning(f"ToDo deletion failed for uid: {todo_uid}")
            return jsonify({"error": "Failed to delete todo"}), 500
            
    except Exception as e:
        logging.error(f"Internal server error in delete_todo: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

@todo.route('/update', methods=['PUT'])
@token_required
def update_todo(current_user_uid):
    """
    Updates a ToDo item by its UID for the authenticated user.
    """

    try:
        todo_uid = request.args.get('todo_uid')
        if not todo_uid:
            logging.warning("Update ToDo failed: todo_uid missing in query parameters")
            return jsonify({'error': 'todo_uid is required in query parameters'}), 400

        data = ToDoUpdateSchema().load(request.get_json())
        task = data.get('task')
        description = data.get('description')
        status = data.get('status')

        updated_todo, error = todo_manager.update_by_uid(todo_uid, current_user_uid, task, description, status)
        if error:
            return jsonify({"error": error}), 404

        return jsonify({
            "message": "Todo updated successfully",
            "todo": ToDoResponseSchema().dump(updated_todo)
        }), 200
    
    except ValidationError as e:
        logging.warning(f"Validation error in update_todo: {e.messages}")
        return jsonify({"error": "Validation error", "details": e.messages}), 400

    except Exception as e:
        logging.error(f"Internal server error in update_todo: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
