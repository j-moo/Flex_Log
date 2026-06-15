from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile


User = get_user_model()


class ProfileAPITests(APITestCase):
    url = '/api/v1/profiles/me/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(self.user)

    def test_get_profile_creates_missing_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'profileuser')
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_update_profile_and_user_name(self):
        response = self.client.patch(
            self.url,
            {'nickname': '플렉스', 'bio': '소비 기록 중', 'name': '홍길동'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(self.user.name, '홍길동')
        self.assertEqual(profile.nickname, '플렉스')
        self.assertEqual(profile.bio, '소비 기록 중')

    def test_profile_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
