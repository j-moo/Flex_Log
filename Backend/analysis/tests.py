from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from expenses.models import Category, ExpenseLog

from .models import MonthlyAIAnalysis, MonthlyAnalysis


User = get_user_model()


class AnalysisModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='analyst', email='analyst@example.com', password='StrongPass123!'
        )

    def test_month_must_be_between_one_and_twelve(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MonthlyAnalysis.objects.create(
                user=self.user,
                year=2026,
                month=13,
                total_amount=0,
            )

    def test_user_has_one_analysis_per_month(self):
        MonthlyAnalysis.objects.create(
            user=self.user,
            year=2026,
            month=6,
            total_amount=100000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            MonthlyAnalysis.objects.create(
                user=self.user,
                year=2026,
                month=6,
                total_amount=200000,
            )


@override_settings(GMS_KEY=None)
class MonthlyAIAnalysisAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='aiuser', email='aiuser@example.com', password='StrongPass123!'
        )
        self.category, _ = Category.objects.get_or_create(name='식비')
        self.client.force_authenticate(self.user)

    def test_create_analysis_uses_fallback_when_gms_key_is_missing(self):
        ExpenseLog.objects.create(
            user=self.user,
            category=self.category,
            amount=120000,
            content='점심과 저녁',
        )

        response = self.client.post(
            '/api/v1/analysis/monthly/',
            {'year': 2026, 'month': 6},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_amount'], 120000)
        self.assertEqual(response.data['log_count'], 1)
        self.assertEqual(response.data['category_summary']['식비']['total'], 120000)
        self.assertTrue(MonthlyAIAnalysis.objects.filter(user=self.user).exists())

    def test_monthly_income_drives_risk_level(self):
        ExpenseLog.objects.create(
            user=self.user,
            category=self.category,
            amount=900000,
            content='수입 대비 큰 지출',
        )

        response = self.client.post(
            '/api/v1/analysis/monthly/',
            {'year': 2026, 'month': 6, 'monthly_income': 1000000},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['risk_level'], 'high')
        self.assertIn('월 수입', response.data['summary'])

    def test_get_monthly_analysis_validates_query_params(self):
        response = self.client.get('/api/v1/analysis/monthly/?year=abc&month=13')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)
        self.assertIn('month', response.data)

    def test_latest_returns_recent_analysis(self):
        MonthlyAIAnalysis.objects.create(
            user=self.user,
            year=2026,
            month=6,
            total_amount=0,
            log_count=0,
            average_amount=0,
            summary='소비 기록이 부족합니다.',
            risk_level='low',
        )

        response = self.client.get('/api/v1/analysis/monthly/latest/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary'], '소비 기록이 부족합니다.')
