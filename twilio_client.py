from flask import current_app
from twilio.rest import Client

def get_twilio_client():
    account_sid = current_app.config["TWILIO_ACCOUNT_SID"]
    auth_token = current_app.config["TWILIO_AUTH_TOKEN"]
    return Client(account_sid, auth_token)
