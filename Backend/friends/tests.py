from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Friend


User = get_user_model()


class FriendModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1', email='user1@example.com', password='StrongPass123!'
        )
        self.friend = User.objects.create_user(
            username='user2', email='user2@example.com', password='StrongPass123!'
        )

    def test_friend_request_cannot_target_self(self):
        with self.assertRaises(ValidationError):
            Friend.objects.create(user=self.user, friend=self.user)

    def test_reverse_friend_request_is_rejected(self):
        Friend.objects.create(user=self.user, friend=self.friend)

        with self.assertRaises(ValidationError):
            Friend.objects.create(user=self.friend, friend=self.user)


class FriendRecommendationAPITests(APITestCase):
    url = '/api/v1/friends/users/?recommend=1'

    def setUp(self):
        self.user = User.objects.create_user(
            username='me', email='me@example.com', password='StrongPass123!'
        )
        self.friend_a = User.objects.create_user(
            username='friend-a', email='friend-a@example.com', password='StrongPass123!'
        )
        self.friend_b = User.objects.create_user(
            username='friend-b', email='friend-b@example.com', password='StrongPass123!'
        )
        self.already_friend = User.objects.create_user(
            username='already', email='already@example.com', password='StrongPass123!'
        )
        self.best_candidate = User.objects.create_user(
            username='candidate-a', email='candidate-a@example.com', password='StrongPass123!'
        )
        self.other_candidate = User.objects.create_user(
            username='candidate-b', email='candidate-b@example.com', password='StrongPass123!'
        )

        Friend.objects.create(user=self.user, friend=self.friend_a, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.user, friend=self.friend_b, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.user, friend=self.already_friend, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.friend_a, friend=self.best_candidate, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.friend_b, friend=self.best_candidate, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.friend_a, friend=self.other_candidate, status=Friend.Status.ACCEPTED)
        Friend.objects.create(user=self.friend_b, friend=self.already_friend, status=Friend.Status.ACCEPTED)
        self.client.force_authenticate(self.user)

    def test_recommends_friends_of_friends_ordered_by_mutual_count(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [item['username'] for item in response.data]
        self.assertEqual(usernames[:2], ['candidate-a', 'candidate-b'])
        self.assertNotIn('already', usernames)
        self.assertEqual(response.data[0]['mutual_friend_count'], 2)
        self.assertEqual(response.data[1]['mutual_friend_count'], 1)

    def test_user_search_does_not_match_private_email(self):
        response = self.client.get('/api/v1/friends/users/?search=candidate-a@example.com')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
