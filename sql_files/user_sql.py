from models import db, User,UserToken

def get_user_by_email(email):
    """
    Retrieves a user by email.
    """
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    """
    Retrieves a user by username.git 
    """
    return User.query.filter_by(username=username).first()

def get_user_by_uid(uid):
    """
    Retrieves a user by UID.
    """
    return User.query.filter_by(uid=uid).first()

def insert_user(user):
    """
    Inserts a new user into the database.
    """
    db.session.add(user)
    db.session.commit()
    return user

def insert_user_token(user_uid, access_token, access_token_expiry, refresh_token, refresh_token_expiry, device_uuid):
    """
    Inserts a new user token record into the database with access and refresh tokens.
    """

    token_record = UserToken(
        user_uid=user_uid,
        access_token=access_token,
        access_token_expiry=access_token_expiry,
        refresh_token=refresh_token,
        refresh_token_expiry=refresh_token_expiry,
        device_uuid=device_uuid
    )
    db.session.add(token_record)
    db.session.commit()
    return token_record

def is_username_taken(username):
    """
    Checks if a username is already taken.
    """
    return db.session.query(User.id).filter_by(username=username).first() is not None

def is_email_registered(email):
    """
    Checks if an email is already registered.
    """
    return db.session.query(User.id).filter_by(email=email).first() is not None

def is_mobile_registered(mobile_number):
    """
    Checks if a mobile number is already registered.
    """
    return db.session.query(User.id).filter_by(mobile_number=mobile_number).first() is not None
