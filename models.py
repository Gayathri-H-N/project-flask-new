import uuid
from datetime import datetime, timezone
from extensions import db
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    create_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # todos = db.relationship('ToDo', backref='user', lazy=True)
    todos = db.relationship(
    'ToDo',
    backref='user',
    lazy=True,
    primaryjoin="User.uid==ToDo.user_uid"
)


class ToDo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    task = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default="in progress", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    modified_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_uid = db.Column(db.String(36),db.ForeignKey('user.uid', name='fk_todo_user_uid'),nullable=False)

   


