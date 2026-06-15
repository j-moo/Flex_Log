from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import MonthlyAnalysis


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
