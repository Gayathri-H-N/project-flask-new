import unittest
import json
from app import create_app
from config import TestConfig
from models import db, User

class ToDoRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Register
            reg_resp = self.client.post(
                "/user/register",
                data=json.dumps({
                    "username": "todouser",
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "todo@example.com",
                    "mobile_number": "9876543210",
                    "password": "TodoPass123@"
                }),
                content_type="application/json"
            )
            print("REGISTER RESPONSE:", reg_resp.status_code, reg_resp.get_data(as_text=True))
            assert reg_resp.status_code == 201, "Registration failed in setUp"

            # Login
            login_resp = self.client.post(
                "/user/login",
                data=json.dumps({
                    "email": "todo@example.com",
                    "password": "TodoPass123@"
                }),
                content_type="application/json"
            )
            login_data = login_resp.get_json()
            print("LOGIN RESPONSE:", login_resp.status_code, login_data)
            assert "access_token" in login_data, f"Access token missing in login response: {login_data}"

            self.token = login_data["access_token"]
            self.auth_headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            self.user_uid = login_data["uid"]
          
    def tearDown(self):
        """This runs AFTER every test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_todo_success(self):
        data = {
            "task": "Buy milk",
            "description": "From the grocery store"
        }
        response = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            headers=self.auth_headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("ToDo created", response.get_json().get("message"))

    def test_create_todo_missing_field(self):
        data = {
            "task": ""
        }
        response = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            headers=self.auth_headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", str(response.get_json()))

    def test_get_todo_success(self):
        # Create a ToDo to retrieve
        self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            headers=self.auth_headers,
            data=json.dumps({
                "task": "Clean Room",
                "description": "Dust and vacuum"
            }),
            content_type='application/json'
        )
        response = self.client.get(
            f'/todo/gettodo?user_uid={self.user_uid}',
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertGreaterEqual(len(response.get_json()), 1)

    def test_update_todo(self):
        # Create ToDo
        res = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            headers=self.auth_headers,
            data=json.dumps({
                "task": "Read book",
                "description": "Finish chapter 1"
            }),
            content_type='application/json'
        )
        todo_uid = res.get_json().get("todo_uid")

        # Update ToDo
        update_data = {
            "task": "Read Python Book",
            "status": "completed"
        }
        response = self.client.put(
            f'/todo/update?todo_uid={todo_uid}',
            headers=self.auth_headers,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Todo updated successfully", response.get_json().get("message"))

    def test_delete_todo(self):
        # Create ToDo
        res = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            headers=self.auth_headers,
            data=json.dumps({
                "task": "Go jogging",
                "description": "Morning jog at 6AM"
            }),
            content_type='application/json'
        )
        todo_uid = res.get_json().get("todo_uid")

        # Delete ToDo
        response = self.client.delete(
            f'/todo/delete?todo_uid={todo_uid}',
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Todo deleted successfully", response.get_json().get("message"))


if __name__ == '__main__':
    unittest.main()
