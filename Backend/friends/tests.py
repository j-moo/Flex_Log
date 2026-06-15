from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

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
