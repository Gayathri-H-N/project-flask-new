from datetime import datetime, timedelta, timezone
from models import db, UserOTP
from flask import current_app


def store_otp(user_uid, otp_code, purpose):
    """
    Stores the generated OTP in the database.
    """
    expiry_minutes = current_app.config.get("OTP_EXPIRY_MINUTES", 5)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
    otp = UserOTP(
        user_uid=user_uid,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False
    )
    db.session.add(otp)
    db.session.commit()


def get_latest_valid_otp(user_uid, otp_code, purpose):
    """
    Gets the latest unused and unexpired OTP for a given user and purpose.
    """
    now = datetime.now(timezone.utc)
    return (
        UserOTP.query
        .filter_by(user_uid=user_uid, purpose=purpose, otp_code=otp_code, is_used=False)
        .filter(UserOTP.expires_at > now)
        .order_by(UserOTP.created_at.desc())
        .first()
    )


def mark_otp_as_used(otp_record):
    """
    Marks the OTP instance as used.
    """
    otp_record.is_used = True
    db.session.commit()


def count_otp_requests_recent(user_uid, purpose, interval_minutes=15):
    now = datetime.now(timezone.utc)
    interval_start = now - timedelta(minutes=interval_minutes)
    return UserOTP.query.filter_by(user_uid=user_uid, purpose=purpose).filter(UserOTP.created_at >= interval_start).count()


def get_latest_unexpired_unused_otp(user_uid, purpose):
    now = datetime.now(timezone.utc)
    return (
        UserOTP.query
        .filter_by(user_uid=user_uid, purpose=purpose, is_used=False)
        .filter(UserOTP.expires_at > now)
        .order_by(UserOTP.created_at.desc())
        .first()
    )
