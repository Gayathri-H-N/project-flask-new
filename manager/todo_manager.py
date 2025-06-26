import logging
from sql_files.todo_sql import insert_todo, get_user_by_uid, get_todos_by_user, delete_todo_by_uid, update_todo_by_uid

class ToDoManager:
    def create(self, task, description, user_uid):
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

    def get_by_user_uid(self, user_uid, date=None):
        user = get_user_by_uid(user_uid)
        if not user:
            logging.warning(f"Get ToDos failed: User with uid {user_uid} not found")
            return None, "User not found"
        todos = get_todos_by_user(user_uid, date)
        logging.info(f"Retrieved {len(todos)} ToDos for user_uid {user_uid}")
        return todos, None

    def delete_by_uid(self, todo_uid):
        if not todo_uid:
            logging.warning("Delete ToDo failed: Todo UID is required")
            return False, "Todo UID is required"

        success = delete_todo_by_uid(todo_uid)
        if not success:
            logging.warning(f"Delete ToDo failed: Todo with uid {todo_uid} not found or could not be deleted")
            return False, "Todo not found or could not be deleted"

        logging.info(f"ToDo with uid {todo_uid} deleted successfully")
        return True, None

    def update_by_uid(self, todo_uid, task=None, description=None, status=None):
        if not todo_uid:
            logging.warning("Update ToDo failed: Todo UID is required")
            return None, "Todo UID is required"

        if not any([task, description, status]):
            logging.warning("Update ToDo failed: No fields provided to update")
            return None, "At least one field must be provided for update"

        updated_todo = update_todo_by_uid(todo_uid, task, description, status)
        if not updated_todo:
            logging.warning(f"Update ToDo failed: Todo with uid {todo_uid} not found")
            return None, "Todo not found"

        logging.info(f"ToDo with uid {todo_uid} updated successfully")
        return updated_todo, None
