from models import db, User

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user_by_uid(uid):
    return User.query.filter_by(uid=uid).first()

def insert_user(user):
    db.session.add(user)
    db.session.commit()
    return user

def is_username_taken(username):
    return db.session.query(User.id).filter_by(username=username).first() is not None

def is_email_registered(email):
    return db.session.query(User.id).filter_by(email=email).first() is not None

def is_mobile_registered(mobile_number):
    return db.session.query(User.id).filter_by(mobile_number=mobile_number).first() is not None
