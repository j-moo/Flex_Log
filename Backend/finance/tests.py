from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import FinancialProduct, StockHolding


User = get_user_model()


class FinanceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='investor', email='investor@example.com', password='StrongPass123!'
        )

    def product_data(self):
        return {
            'product_code': 'DP001',
            'product_name': '테스트 예금',
            'bank_name': '테스트 은행',
            'product_type': FinancialProduct.ProductType.DEPOSIT,
            'base_rate': Decimal('2.500'),
            'max_rate': Decimal('3.000'),
            'save_term': 12,
        }

    def test_product_code_is_unique(self):
        FinancialProduct.objects.create(**self.product_data())

        with self.assertRaises(IntegrityError), transaction.atomic():
            FinancialProduct.objects.create(**self.product_data())

    def test_stock_symbol_is_saved_in_uppercase(self):
        holding = StockHolding.objects.create(
            user=self.user,
            stock_symbol='aapl',
            stock_name='Apple',
            quantity=2,
            average_price=Decimal('210.5000'),
        )

        self.assertEqual(holding.stock_symbol, 'AAPL')
