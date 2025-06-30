import unittest
import json
from config import TestConfig
from app import create_app
from models import db, User

class UserRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
       
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user_success(self):
        payload = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "mobile_number": "9876543210",
            "password": "MyPass@123"
        }
        response = self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered", response.get_json().get("message"))

    def test_register_duplicate_email(self):
        payload = {
            "username": "uniqueuser",
            "first_name": "First",
            "last_name": "Last",
            "email": "duplicate@example.com",
            "mobile_number": "9876543211",
            "password": "Pass1234!"
        }
        self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        payload["username"] = "otheruser"
        payload["mobile_number"] = "9876543212"
        response = self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_login_user_success(self):
        payload = {
            "username": "loginuser",
            "first_name": "Login",
            "last_name": "User",
            "email": "login@example.com",
            "mobile_number": "9876543213",
            "password": "LoginPass2$"
        }
        self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')

        login_payload = {
            "email": "login@example.com",
            "password": "LoginPass2$"
        }
        response = self.client.post('/user/login', data=json.dumps(login_payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome", response.get_json().get("message"))

    def test_login_user_invalid_password(self):
        login_payload = {
            "email": "wrong@example.com",
            "password": "WrongPass1!"
        }
        response = self.client.post('/user/login', data=json.dumps(login_payload), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_json().get("error"))

    def test_register_invalid_email_format(self):
        payload = {
            "username": "invalidemail",
            "first_name": "Email",
            "last_name": "Format",
            "email": "invalidemail",
            "mobile_number": "9876543214",
            "password": "Pass1234!"
        }
        response = self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.get_json())

    def test_register_missing_password(self):
        payload = {
            "username": "nopassword",
            "first_name": "No",
            "last_name": "Pass",
            "email": "nopass@example.com",
            "mobile_number": "9876543215"
        }
        response = self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.get_json())

    def test_register_short_username(self):
        payload = {
            "username": "ab",
            "first_name": "Short",
            "last_name": "Name",
            "email": "short@example.com",
            "mobile_number": "9876543216",
            "password": "Pass1234!"
        }
        response = self.client.post('/user/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.get_json())

    def test_register_duplicate_mobile_number(self):
        payload1 = {
            "username": "mobuser1",
            "first_name": "Mob",
            "last_name": "User",
            "email": "mob1@example.com",
            "mobile_number": "7777777777",
            "password": "Pass1234!"
        }
        payload2 = {
            "username": "mobuser2",
            "first_name": "Mob",
            "last_name": "User",
            "email": "mob2@example.com",
            "mobile_number": "7777777777",
            "password": "Pass1234!"
        }
        self.client.post('/user/register', data=json.dumps(payload1), content_type='application/json')
        response = self.client.post('/user/register', data=json.dumps(payload2), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

if __name__ == '__main__':
    unittest.main()
