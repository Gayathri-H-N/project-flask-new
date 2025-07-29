from twilio.rest import Client
import os

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)

TWILIO_FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") 

def get_twilio_client():
    return twilio_client

