import logging
from sql_files.todo_sql import (
    insert_todo,
    get_user_by_uid,
    get_todos_by_user,
    delete_todo_by_uid,
    update_todo_by_uid,
)

class ToDoManager:
    def create(self, task, description, user_uid):
        """
        Contains the logic to create a new ToDo item for a user after validating input and user existence.
        """

        try:
            if not task or not user_uid:
                logging.warning("Create ToDo failed: Task and user_uid are required")
                return None, "Task and user_uid are required"

            user = get_user_by_uid(user_uid)
            if not user:
                logging.warning(f"Create ToDo failed: User with uid {user_uid} does not exist")
                return None, "User does not exist"

            todo = insert_todo(task, description, user_uid)
            logging.info(f"ToDo created successfully for user_uid {user_uid} with task: {task}")
            return todo, None

        except Exception as e:
            logging.error(f"Unexpected error in create: {str(e)}")
            return None, "Internal server error"


    def get_by_user_uid(self, user_uid, date=None):
        """
        Contains the logic to retrieve ToDo items for a user, with optional filtering by date.
        """

        try:
            user = get_user_by_uid(user_uid)
            if not user:
                logging.warning(f"Get ToDos failed: User with uid {user_uid} not found")
                return None, "User not found"
            todos = get_todos_by_user(user_uid, date)
            logging.info(f"Retrieved {len(todos)} ToDos for user_uid {user_uid}")
            return todos, None

        except Exception as e:
            logging.error(f"Unexpected error in get_by_user_uid: {str(e)}")
            return None, "Internal server error"


    def delete_by_uid(self, todo_uid, user_uid):
        """
        Contains the logic to delete a ToDo item by its UID for a specific user.
        """

        try:
            if not todo_uid:
                logging.warning("Delete ToDo failed: Todo UID is required")
                return False, "Todo UID is required"

            success = delete_todo_by_uid(todo_uid, user_uid)
            if not success:
                logging.warning(f"Delete ToDo failed: Todo with uid {todo_uid} not found for user {user_uid}")
                return False, "Todo not found or could not be deleted"

            logging.info(f"ToDo with uid {todo_uid} deleted successfully")
            return True, None

        except Exception as e:
            logging.error(f"Unexpected error in delete_by_uid: {str(e)}")
            return False, "Internal server error"


    def update_by_uid(self, todo_uid, user_uid, task=None, description=None, status=None):
        """
        Contains the logic to update fields of a ToDo item by its UID for a specific user.
        """

        try:
            if not todo_uid:
                logging.warning("Update ToDo failed: Todo UID is required")
                return None, "Todo UID is required"

            if not any([task, description, status]):
                logging.warning("Update ToDo failed: No fields provided to update")
                return None, "At least one field must be provided for update"

            updated_todo = update_todo_by_uid(todo_uid, user_uid, task, description, status)
            if not updated_todo:
                logging.warning(f"Update ToDo failed: Todo with uid {todo_uid} not found for user {user_uid}")
                return None, "Todo not found or unauthorized"

            logging.info(f"ToDo with uid {todo_uid} updated successfully for user {user_uid}")
            return updated_todo, None

        except Exception as e:
            logging.error(f"Unexpected error in update_by_uid: {str(e)}")
            return None, "Internal server error"
