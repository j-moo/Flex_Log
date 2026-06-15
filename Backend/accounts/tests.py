from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from profiles.models import Profile


User = get_user_model()


class SignUpAPITests(APITestCase):
    url = '/api/v1/accounts/signup/'

    def payload(self, **overrides):
        data = {
            'username': 'flexuser',
            'email': 'flex@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        data.update(overrides)
        return data

    def test_signup_creates_user_profile_and_tokens(self):
        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='flexuser')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_signup_requires_email(self):
        data = self.payload()
        data.pop('email')

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_rejects_duplicate_username(self):
        User.objects.create_user(
            username='flexuser',
            email='other@example.com',
            password='StrongPass123!',
        )

        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_signup_rejects_duplicate_email_ignoring_case(self):
        User.objects.create_user(
            username='other',
            email='Flex@Example.com',
            password='StrongPass123!',
        )

        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_rejects_password_mismatch(self):
        response = self.client.post(
            self.url,
            self.payload(password_confirm='DifferentPass123!'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_signup_applies_django_password_validation(self):
        response = self.client.post(
            self.url,
            self.payload(password='1234', password_confirm='1234'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
