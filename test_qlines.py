import unittest
from qlines import app


class SignupTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_signup_success(self):
        response = self.app.post('/signup', data={
            'email': 'test@example.com',
            'agreeterms': 'on',
            'password_main': 'password',
            'password_confirm': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'confirm_registration.html', response.data)

    def test_signup_password_mismatch(self):
        response = self.app.post('/signup', data={
            'email': 'test@example.com',
            'agreeterms': 'on',
            'password_main': 'password',
            'password_confirm': 'notpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match!', response.data)

    def test_signup_terms_not_checked(self):
        response = self.app.post('/signup', data={
            'email': 'test@example.com',
            'agreeterms': '',
            'password_main': 'password',
            'password_confirm': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please read the terms and conditions.', response.data)

    def test_signup_user_already_exists(self):
        response = self.app.post('/signup', data={
            'email': 'test@example.com',
            'agreeterms': 'on',
            'password_main': 'password',
            'password_confirm': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The user already exists!', response.data)