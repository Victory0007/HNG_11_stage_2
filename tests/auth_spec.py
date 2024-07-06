import unittest
import json
from app.main import create_app, db


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Register and login a user to get an access token
        self.user_registration_data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "password": "password123",
            "phone": "0987654321"
        }
        self.client().post('/auth/register', json=self.user_registration_data)
        response = self.client().post('/auth/login', json={
            "email": "jane@example.com",
            "password": "password123"
        })

        response_data = json.loads(response.data)
        self.access_token = response_data['data'].get('accessToken') or response_data['data'].get('access_token')
        if not self.access_token:
            raise KeyError("accessToken or access_token not found in response data")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        response = self.client().post('/auth/register', json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "1234567890"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('accessToken', data['data'])
        self.assertIn('user', data['data'])

    def test_user_login(self):
        # First, register a user
        self.client().post('/auth/register', json={
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "password": "password123",
            "phone": "0987654321"
        })
        # Then, login with the same user
        response = self.client().post('/auth/login', json={
            "email": "jane@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data['data'])
        self.assertIn('user', data['data'])

    def test_get_user_details(self):
        # First, register a user
        response = self.client().post('/auth/register', json={
            "firstName": "Jake",
            "lastName": "Smith",
            "email": "jake@example.com",
            "password": "password123",
            "phone": "1231231234"
        })
        data = json.loads(response.data)
        token = data['data']['accessToken']
        user_id = data['data']['user']['userId']

        # Get user details
        response = self.client().get(f'/api/users/{user_id}', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['userId'], user_id)

    def test_get_organisations(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.client().get('/api/organisations', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data['data']['organisations']), 0)

    def test_create_organisation(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        payload = {
            "name": "Jane's New Organisation",
            "description": "This is a new organisation"
        }
        response = self.client().post('/api/organisations', headers=headers, json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['name'], "Jane's New Organisation")

    def test_get_specific_organisation(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.client().get('/api/organisations', headers=headers)
        orgs = json.loads(response.data)['data']['organisations']
        org_id = orgs[0]['orgId']

        response = self.client().get(f'/api/organisations/{org_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['orgId'], org_id)

    def test_add_user_to_organisation(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        # Assuming organization creation is part of your setup
        response = self.client().post('/api/organisations', headers=headers, json={
            "name": "Test Organisation",
            "description": "This is a test organisation"
        })
        org_id = json.loads(response.data)['data']['orgId']

        # Assuming we have another user registered
        another_user_payload = {
            "firstName": "Jake",
            "lastName": "Doe",
            "email": "jake.doe@example.com",
            "password": "password123",
            "phone": "0987654321"
        }
        self.client().post('/auth/register', json=another_user_payload)

        # Get the userId of the newly registered user
        response = self.client().post('/auth/login', json={
            "email": "jake.doe@example.com",
            "password": "password123"
        })
        another_user_data = json.loads(response.data)
        another_user_id = another_user_data['data']['user']['userId']

        # Add the new user to the organisation
        add_user_payload = {
            "userId": another_user_id
        }
        response = self.client().post(f'/api/organisations/{org_id}/users', headers=headers, json=add_user_payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'User added to organisation successfully')


if __name__ == "__main__":
    unittest.main()
