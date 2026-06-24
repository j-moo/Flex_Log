from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .recommendation_utils import create_financial_product_recommendations
from .models import (
    Commodity,
    CommodityPrice,
    FinancialProduct,
    FinancialProductOption,
    StockHolding,
    UserFinancialProduct,
)


class FinanceModelRegistrationTests(SimpleTestCase):
    def test_finance_models_are_registered(self):
        model_names = {
            model.__name__
            for model in apps.get_app_config('finance').get_models()
        }

        self.assertIn('FinancialProduct', model_names)
        self.assertIn('FinancialProductOption', model_names)
        self.assertIn('FinancialProductRecommendation', model_names)
        self.assertIn('UserFinancialProduct', model_names)
        self.assertIn('Commodity', model_names)
        self.assertIn('CommodityPrice', model_names)


class UserFinancialProductTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='subscriber',
            email='subscriber@example.com',
            password='StrongPass123!',
        )
        self.product = FinancialProduct.objects.create(
            product_type='deposit',
            fin_prdt_cd='TEST001',
            kor_co_nm='테스트은행',
            fin_prdt_nm='테스트예금',
        )
        self.option = FinancialProductOption.objects.create(
            product=self.product,
            save_trm=12,
            intr_rate='2.5000',
            intr_rate2='3.0000',
        )

    def test_same_option_cannot_be_joined_twice(self):
        UserFinancialProduct.objects.create(user=self.user, option=self.option)

        with self.assertRaises(IntegrityError), transaction.atomic():
            UserFinancialProduct.objects.create(user=self.user, option=self.option)

    def test_cancelled_subscription_requires_cancelled_at(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            UserFinancialProduct.objects.create(
                user=self.user,
                option=self.option,
                status=UserFinancialProduct.Status.CANCELLED,
            )


class UserFinancialProductAPITests(APITestCase):
    url = '/api/v1/finance/subscriptions/'

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='api-subscriber',
            email='api-subscriber@example.com',
            password='StrongPass123!',
        )
        self.other_user = get_user_model().objects.create_user(
            username='other-subscriber',
            email='other-subscriber@example.com',
            password='StrongPass123!',
        )
        self.product = FinancialProduct.objects.create(
            product_type='deposit',
            fin_prdt_cd='API001',
            kor_co_nm='API은행',
            fin_prdt_nm='API예금',
        )
        self.option = FinancialProductOption.objects.create(
            product=self.product,
            save_trm=12,
            intr_rate='2.5000',
            intr_rate2='3.0000',
        )
        self.client.force_authenticate(self.user)

    def test_join_cancel_and_rejoin_product(self):
        response = self.client.post(self.url, {'option_id': self.option.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        subscription_id = response.data['id']

        duplicate_response = self.client.post(
            self.url, {'option_id': self.option.id}, format='json',
        )
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

        cancel_response = self.client.post(
            f'{self.url}{subscription_id}/cancel/', {}, format='json',
        )
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_response.data['status'], UserFinancialProduct.Status.CANCELLED)

        rejoin_response = self.client.post(
            self.url, {'option_id': self.option.id}, format='json',
        )
        self.assertEqual(rejoin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rejoin_response.data['id'], subscription_id)
        self.assertEqual(rejoin_response.data['status'], UserFinancialProduct.Status.ACTIVE)

    def test_user_cannot_cancel_another_users_subscription(self):
        subscription = UserFinancialProduct.objects.create(
            user=self.other_user,
            option=self.option,
        )
        response = self.client.post(
            f'{self.url}{subscription.id}/cancel/', {}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommodityPriceAPITests(APITestCase):
    import_url = '/api/v1/finance/commodities/prices/import/'

    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='price-admin',
            email='price-admin@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.user = get_user_model().objects.create_user(
            username='price-user',
            email='price-user@example.com',
            password='StrongPass123!',
        )
        self.payload = {
            'code': 'GOLD',
            'source': 'test-source',
            'prices': [
                {
                    'price_date': '2026-06-20',
                    'open_price': '2300.000000',
                    'high_price': '2350.000000',
                    'low_price': '2290.000000',
                    'close_price': '2340.000000',
                },
                {
                    'price_date': '2026-06-21',
                    'close_price': '2360.000000',
                },
            ],
        }

    def test_admin_can_import_and_update_prices(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.import_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 2)

        self.payload['prices'] = [
            {'price_date': '2026-06-21', 'close_price': '2370.000000'},
        ]
        response = self.client.post(self.import_url, self.payload, format='json')
        self.assertEqual(response.data['updated'], 1)
        self.assertEqual(CommodityPrice.objects.count(), 2)

    def test_authenticated_user_can_query_date_range(self):
        commodity = Commodity.objects.create(
            code='SILVER', name='은', unit='USD/troy oz',
        )
        CommodityPrice.objects.create(
            commodity=commodity, price_date='2026-06-20', close_price='30.000000',
        )
        CommodityPrice.objects.create(
            commodity=commodity, price_date='2026-06-21', close_price='31.000000',
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(
            '/api/v1/finance/commodities/SILVER/prices/?start=2026-06-21&end=2026-06-21',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['prices']), 1)
        self.assertEqual(response.data['prices'][0]['price_date'], '2026-06-21')

    def test_non_admin_cannot_import_prices(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.import_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(GMS_KEY=None)
class FinancialRecommendationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='recommend-user',
            email='recommend@example.com',
            password='StrongPass123!',
        )

    def test_recommendations_include_same_product_once(self):
        product = FinancialProduct.objects.create(
            product_type='deposit',
            fin_prdt_cd='RECO001',
            kor_co_nm='Test Bank',
            fin_prdt_nm='Multi Option Deposit',
        )
        lower_option = FinancialProductOption.objects.create(
            product=product,
            save_trm=6,
            intr_rate='2.0000',
            intr_rate2='2.5000',
        )
        best_option = FinancialProductOption.objects.create(
            product=product,
            save_trm=12,
            intr_rate='3.0000',
            intr_rate2='3.8000',
        )

        recommendations = create_financial_product_recommendations(self.user)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_id, product.id)
        self.assertEqual(recommendations[0].option_id, best_option.id)
        self.assertNotEqual(recommendations[0].option_id, lower_option.id)


class StockHoldingAPITests(APITestCase):
    url = '/api/v1/finance/stocks/'

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='stock-user',
            email='stock-user@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(self.user)

    def test_duplicate_symbol_post_merges_quantity_and_average_price(self):
        first = self.client.post(
            self.url,
            {
                'symbol': '005930',
                'name': '삼성전자',
                'quantity': 2,
                'average_price': '60000.00',
                'current_price': '65000.00',
            },
            format='json',
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(
            self.url,
            {
                'symbol': '005930',
                'name': '삼성전자',
                'quantity': 3,
                'average_price': '70000.00',
                'current_price': '72000.00',
            },
            format='json',
        )

        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(StockHolding.objects.filter(user=self.user, symbol='005930').count(), 1)
        holding = StockHolding.objects.get(user=self.user, symbol='005930')
        self.assertEqual(str(holding.quantity), '5.0000')
        self.assertEqual(str(holding.average_price), '66000.00')
        self.assertEqual(float(second.data['valuation_amount']), 360000.0)

    def test_delete_stock_holding_can_subtract_quantity(self):
        holding = StockHolding.objects.create(
            user=self.user,
            symbol='AAPL',
            name='Apple',
            quantity='5.0000',
            average_price='100.00',
            current_price='120.00',
        )

        response = self.client.delete(
            f'{self.url}{holding.id}/',
            {'quantity': 2},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        holding.refresh_from_db()
        self.assertEqual(str(holding.quantity), '3.0000')
        self.assertEqual(float(response.data['valuation_amount']), 360.0)

    def test_delete_stock_holding_rejects_excess_quantity(self):
        holding = StockHolding.objects.create(
            user=self.user,
            symbol='MSFT',
            name='Microsoft',
            quantity='1.0000',
            average_price='100.00',
            current_price='120.00',
        )

        response = self.client.delete(
            f'{self.url}{holding.id}/',
            {'quantity': 2},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(StockHolding.objects.filter(pk=holding.id).exists())

    def test_delete_stock_holding_rejects_decimal_quantity(self):
        holding = StockHolding.objects.create(
            user=self.user,
            symbol='NVDA',
            name='NVIDIA',
            quantity='3.0000',
            average_price='100.00',
            current_price='120.00',
        )

        response = self.client.delete(
            f'{self.url}{holding.id}/',
            {'quantity': '1.5'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        holding.refresh_from_db()
        self.assertEqual(str(holding.quantity), '3.0000')


class ExternalDiscoveryAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='discovery-user',
            email='discovery@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(self.user)

    @patch('finance.views.search_videos')
    def test_youtube_search_returns_normalized_videos(self, search_mock):
        search_mock.return_value = [
            {'video_id': 'abc123', 'title': '금리 전망', 'channel_title': '채널'},
        ]
        response = self.client.get('/api/v1/finance/youtube/search/?q=금리')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['videos'][0]['video_id'], 'abc123')
        search_mock.assert_called_once_with('금리', 12)

    @patch('finance.views.get_video_detail')
    def test_youtube_detail_returns_video(self, detail_mock):
        detail_mock.return_value = {'video_id': 'abc123', 'title': '금리 전망'}
        response = self.client.get('/api/v1/finance/youtube/videos/abc123/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '금리 전망')

    @patch('finance.views.search_nearby_banks')
    def test_nearby_bank_search_returns_center_and_banks(self, bank_mock):
        bank_mock.return_value = {
            'center': {'name': '역삼역', 'x': 127.0, 'y': 37.5},
            'banks': [{'id': '1', 'name': '테스트은행', 'distance': 100}],
        }
        response = self.client.get('/api/v1/finance/banks/nearby/?query=역삼역')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['banks'][0]['name'], '테스트은행')
        bank_mock.assert_called_once_with('역삼역', 2000)

    @patch('finance.views.search_driving_route')
    def test_bank_route_returns_polyline_path(self, route_mock):
        route_mock.return_value = {
            'origin': {'name': '멀티캠퍼스 역삼', 'x': 127.039585, 'y': 37.5012743},
            'destination': {'name': '테스트은행', 'x': 127.0, 'y': 37.5},
            'summary': {'distance': 1200, 'duration': 600, 'fare': {}},
            'path': [{'x': 127.039585, 'y': 37.5012743}, {'x': 127.0, 'y': 37.5}],
        }
        response = self.client.get('/api/v1/finance/banks/route/?x=127.0&y=37.5&name=테스트은행')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['path']), 2)
        route_mock.assert_called_once_with(127.0, 37.5, '테스트은행')

    def test_discovery_queries_are_required(self):
        youtube_response = self.client.get('/api/v1/finance/youtube/search/')
        bank_response = self.client.get('/api/v1/finance/banks/nearby/')
        route_response = self.client.get('/api/v1/finance/banks/route/')
        self.assertEqual(youtube_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(bank_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(route_response.status_code, status.HTTP_400_BAD_REQUEST)
