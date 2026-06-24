from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, ExpenseLog, Like


User = get_user_model()
DELETE_CONFIRM_TEXT = (
    '정말 삭제하시겠습니까? 이거 삭제하면 로그 날아감 지인짜로오. '
    'AI 분석이랑 소비 통계에도 영향을 끼칩니다. 삭제된 피드는 복구할 수 없고, '
    '월별 소비 분석과 추천 결과도 달라질 수 있습니다.'
)


def delete_confirmation_payload(code='4827'):
    return {
        'confirmation_code': code,
        'confirmation_text': f'{DELETE_CONFIRM_TEXT} 확인코드: {code}',
    }


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='spender', email='spender@example.com', password='StrongPass123!'
        )
        self.category, _ = Category.objects.get_or_create(name='식비')

    def test_expense_amount_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpenseLog.objects.create(
                user=self.user,
                category=self.category,
                amount=0,
            )

    def test_user_can_like_expense_only_once(self):
        expense = ExpenseLog.objects.create(
            user=self.user,
            category=self.category,
            amount=12000,
        )
        Like.objects.create(user=self.user, log=expense)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Like.objects.create(user=self.user, log=expense)

    def test_expense_is_visible_before_expiration(self):
        expense = ExpenseLog.objects.create(
            user=self.user,
            category=self.category,
            amount=12000,
        )

        self.assertTrue(expense.is_feed_visible)


class ExpenseAPITests(APITestCase):
    list_url = '/api/v1/expenses/'
    category_url = '/api/v1/expenses/categories/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser', email='apiuser@example.com', password='StrongPass123!'
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='StrongPass123!'
        )
        self.category = Category.objects.create(name='테스트 카테고리')
        self.client.force_authenticate(self.user)

    def test_list_categories(self):
        response = self.client.get(self.category_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('테스트 카테고리', [item['name'] for item in response.data])

    def test_create_expense_assigns_authenticated_user(self):
        response = self.client.post(
            self.list_url,
            {
                'category': self.category.id,
                'title': '점심 식사',
                'amount': 15000,
                'content': '점심 식사',
                'is_visible': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = ExpenseLog.objects.get(pk=response.data['id'])
        self.assertEqual(expense.user, self.user)
        self.assertEqual(response.data['category_name'], '테스트 카테고리')

    def test_list_contains_only_own_expenses(self):
        own_expense = ExpenseLog.objects.create(
            user=self.user, category=self.category, amount=10000
        )
        ExpenseLog.objects.create(
            user=self.other_user, category=self.category, amount=20000
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [own_expense.id])

    def test_update_own_expense(self):
        expense = ExpenseLog.objects.create(
            user=self.user, category=self.category, amount=10000
        )

        response = self.client.patch(
            f'{self.list_url}{expense.id}/',
            {'amount': 18000, 'content': '수정된 로그'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, 18000)
        self.assertEqual(expense.content, '수정된 로그')

    def test_cannot_access_other_users_expense(self):
        expense = ExpenseLog.objects.create(
            user=self.other_user, category=self.category, amount=20000
        )

        response = self.client.get(f'{self.list_url}{expense.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_expense(self):
        expense = ExpenseLog.objects.create(
            user=self.user, category=self.category, amount=10000
        )

        response = self.client.delete(
            f'{self.list_url}{expense.id}/',
            delete_confirmation_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ExpenseLog.objects.filter(pk=expense.id).exists())

    def test_delete_requires_confirmation_text(self):
        expense = ExpenseLog.objects.create(
            user=self.user, category=self.category, amount=10000
        )

        response = self.client.delete(
            f'{self.list_url}{expense.id}/',
            {
                'confirmation_code': '4827',
                'confirmation_text': '틀린 문구',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ExpenseLog.objects.filter(pk=expense.id).exists())

    def test_delete_confirmation_allows_line_breaks_and_outer_spaces(self):
        expense = ExpenseLog.objects.create(
            user=self.user, category=self.category, amount=10000
        )

        response = self.client.delete(
            f'{self.list_url}{expense.id}/',
            {
                'confirmation_code': '4827',
                'confirmation_text': (
                    f'  {DELETE_CONFIRM_TEXT}\n\n'
                    '확인코드: 4827  '
                ),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ExpenseLog.objects.filter(pk=expense.id).exists())

    def test_cannot_delete_other_users_expense(self):
        expense = ExpenseLog.objects.create(
            user=self.other_user, category=self.category, amount=20000
        )

        response = self.client.delete(
            f'{self.list_url}{expense.id}/',
            delete_confirmation_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ExpenseLog.objects.filter(pk=expense.id).exists())

    def test_expenses_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
