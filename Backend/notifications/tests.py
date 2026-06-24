from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from expenses.models import Category, ExpenseLog

from .models import Notification


User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='notification-user',
            email='notification@example.com',
            password='StrongPass123!',
        )
        self.actor = User.objects.create_user(
            username='notification-actor',
            email='notification-actor@example.com',
            password='StrongPass123!',
        )
        self.second_actor = User.objects.create_user(
            username='second-actor',
            email='second-actor@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(self.user)

    def test_unread_count_and_mark_read(self):
        notification = Notification.objects.create(
            user=self.user,
            actor=self.actor,
            notification_type=Notification.Type.FRIEND_REQUEST,
            title='친구 요청',
            message='친구 요청이 도착했습니다.',
            target_route='friends',
        )

        count_response = self.client.get('/api/v1/notifications/unread-count/')
        self.assertEqual(count_response.status_code, status.HTTP_200_OK)
        self.assertEqual(count_response.data['unread_count'], 1)

        list_response = self.client.get('/api/v1/notifications/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data[0]['target_route'], 'friends')

        read_response = self.client.patch(f'/api/v1/notifications/{notification.id}/read/')
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertTrue(read_response.data['is_read'])

        count_response = self.client.get('/api/v1/notifications/unread-count/')
        self.assertEqual(count_response.data['unread_count'], 0)

    def test_liking_another_users_feed_creates_notification(self):
        category = Category.objects.create(name='알림 테스트')
        log = ExpenseLog.objects.create(
            user=self.user,
            category=category,
            amount=10000,
            visibility=ExpenseLog.Visibility.PUBLIC,
            is_visible=True,
        )
        self.client.force_authenticate(self.actor)

        response = self.client.post(f'/api/v1/expenses/{log.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification = Notification.objects.get(user=self.user)
        self.assertEqual(notification.notification_type, Notification.Type.LIKE)
        self.assertEqual(notification.target_route, 'log-detail')
        self.assertEqual(notification.target_params, {'id': log.id})
        self.assertEqual(notification.title, '좋아요 1명')
        self.assertEqual(notification.message, '@notification-actor님이 내 피드에 좋아요를 눌렀습니다.')

    def test_likes_on_same_feed_update_one_grouped_notification(self):
        category = Category.objects.create(name='좋아요 그룹')
        log = ExpenseLog.objects.create(
            user=self.user,
            category=category,
            amount=10000,
            visibility=ExpenseLog.Visibility.PUBLIC,
            is_visible=True,
        )

        self.client.force_authenticate(self.actor)
        self.client.post(f'/api/v1/expenses/{log.id}/like/')
        self.client.force_authenticate(self.second_actor)
        self.client.post(f'/api/v1/expenses/{log.id}/like/')

        notifications = Notification.objects.filter(user=self.user, notification_type=Notification.Type.LIKE)
        self.assertEqual(notifications.count(), 1)
        notification = notifications.get()
        self.assertEqual(notification.title, '좋아요 2명')
        self.assertEqual(notification.message, '@notification-actor님 외 1명이 내 피드에 좋아요를 눌렀습니다.')

    def test_comments_on_same_feed_update_one_grouped_notification_by_commenter(self):
        category = Category.objects.create(name='댓글 그룹')
        log = ExpenseLog.objects.create(
            user=self.user,
            category=category,
            amount=10000,
            visibility=ExpenseLog.Visibility.PUBLIC,
            is_visible=True,
        )

        self.client.force_authenticate(self.actor)
        self.client.post(f'/api/v1/expenses/{log.id}/comments/', {'content': '첫 댓글'}, format='json')
        self.client.post(f'/api/v1/expenses/{log.id}/comments/', {'content': '같은 사람 댓글'}, format='json')
        self.client.force_authenticate(self.second_actor)
        self.client.post(f'/api/v1/expenses/{log.id}/comments/', {'content': '다른 사람 댓글'}, format='json')

        notifications = Notification.objects.filter(user=self.user, notification_type=Notification.Type.COMMENT)
        self.assertEqual(notifications.count(), 1)
        notification = notifications.get()
        self.assertEqual(notification.title, '댓글 2명')
        self.assertEqual(notification.message, '@notification-actor님 외 1명이 내 피드에 댓글을 남겼습니다.')
