from models import db, ToDo, User
from datetime import datetime, timezone
from sqlalchemy import func

def insert_todo(task, description, user_uid):
    todo = ToDo(task=task, description=description, user_uid=user_uid)
    db.session.add(todo)
    db.session.commit()
    return todo

def get_user_by_uid(user_uid):
    return User.query.filter_by(uid=user_uid).first()

def get_todos_by_user(user_uid, date=None):
    query = ToDo.query.filter_by(user_uid=user_uid)
    if date:
        query = query.filter(func.date(ToDo.created_at) == date)
    return query.order_by(ToDo.created_at.desc()).all()

def delete_todo_by_uid(todo_uid, user_uid):
    todo = ToDo.query.filter_by(uid=todo_uid, user_uid=user_uid).first()    
    if not todo:
        return False
    db.session.delete(todo)
    db.session.commit()
    return True

def update_todo_by_uid(todo_uid, user_uid, task=None, description=None, status=None):
    todo = ToDo.query.filter_by(uid=todo_uid, user_uid=user_uid).first()
    if not todo:
        return None

    if task is not None:
        todo.task = task
    if description is not None:
        todo.description = description
    if status is not None:
        todo.status = status

    todo.modified_at = datetime.now(timezone.utc)
    db.session.commit()
    return todo