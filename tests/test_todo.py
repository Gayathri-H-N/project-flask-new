import unittest
import json
from config import TestConfig
from app import create_app
from models import db, User, ToDo


class ToDoRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            # A user for ToDo testing
            response = self.client.post('/user/register', data=json.dumps({
                "username": "todouser",
                "first_name": "Test",
                "last_name": "User",
                "email": "todo@example.com",
                "mobile_number": "9876543210",
                "password": "TodoPass123"
            }), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.user_uid = User.query.filter_by(username="todouser").first().uid

    def tearDown(self):
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
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", str(response.get_json()))

    def test_get_todo_success(self):
        self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            data=json.dumps({
                "task": "Clean Room",
                "description": "Dust and vacuum"
            }),
            content_type='application/json'
        )
        response = self.client.get(f'/todo/gettodo?user_uid={self.user_uid}')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertGreaterEqual(len(response.get_json()), 1)

    def test_update_todo(self):
        res = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            data=json.dumps({
                "task": "Read book",
                "description": "Finish chapter 1"
            }),
            content_type='application/json'
        )
        todo_uid = res.get_json().get("todo_uid")
        update_data = {
            "task": "Read Python Book",
            "status": "completed"
        }
        response = self.client.put(
            f'/todo/update?todo_uid={todo_uid}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Todo updated successfully", response.get_json().get("message"))

    def test_delete_todo(self):
        res = self.client.post(
            f'/todo/create?user_uid={self.user_uid}',
            data=json.dumps({
                "task": "Go jogging",
                "description": "Morning jog at 6AM"
            }),
            content_type='application/json'
        )
        todo_uid = res.get_json().get("todo_uid")
        response = self.client.delete(f'/todo/delete?todo_uid={todo_uid}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Todo deleted successfully", response.get_json().get("message"))


if __name__ == '__main__':
    unittest.main()
