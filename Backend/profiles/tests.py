from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from friends.models import Friend
from finance.models import FinancialProduct, FinancialProductOption, UserFinancialProduct

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
        self.assertEqual(response.data['email'], 'profile@example.com')
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

    def test_profile_contains_only_active_joined_products(self):
        product = FinancialProduct.objects.create(
            product_type='saving',
            fin_prdt_cd='PROFILE001',
            kor_co_nm='프로필은행',
            fin_prdt_nm='프로필적금',
        )
        active_option = FinancialProductOption.objects.create(
            product=product,
            save_trm=12,
            intr_rate='3.0000',
            intr_rate2='3.5000',
        )
        cancelled_option = FinancialProductOption.objects.create(
            product=product,
            save_trm=24,
            intr_rate='3.2000',
            intr_rate2='3.7000',
        )
        UserFinancialProduct.objects.create(user=self.user, option=active_option)
        UserFinancialProduct.objects.create(
            user=self.user,
            option=cancelled_option,
            status=UserFinancialProduct.Status.CANCELLED,
            cancelled_at='2026-06-22T00:00:00Z',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['joined_products']), 1)
        self.assertEqual(
            response.data['joined_products'][0]['option']['id'],
            active_option.id,
        )
    def test_public_profile_hides_joined_products_from_non_friend(self):
        other = User.objects.create_user(
            username='product-owner',
            email='owner@example.com',
            password='StrongPass123!',
        )
        Profile.objects.create(user=other, nickname='owner')
        product = FinancialProduct.objects.create(
            product_type='saving',
            fin_prdt_cd='PUBLIC001',
            kor_co_nm='Test Bank',
            fin_prdt_nm='Hidden Saving',
        )
        option = FinancialProductOption.objects.create(
            product=product,
            save_trm=12,
            intr_rate='3.0000',
            intr_rate2='3.5000',
        )
        UserFinancialProduct.objects.create(user=other, option=option)

        response = self.client.get(f'/api/v1/profiles/{other.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('email', response.data)
        self.assertFalse(response.data['can_view_joined_products'])
        self.assertEqual(response.data['joined_products'], [])

    def test_public_profile_shows_joined_products_to_friend(self):
        other = User.objects.create_user(
            username='friend-owner',
            email='friend-owner@example.com',
            password='StrongPass123!',
        )
        Profile.objects.create(user=other, nickname='friend-owner')
        Friend.objects.create(
            user=self.user,
            friend=other,
            status=Friend.Status.ACCEPTED,
        )
        product = FinancialProduct.objects.create(
            product_type='deposit',
            fin_prdt_cd='PUBLIC002',
            kor_co_nm='Test Bank',
            fin_prdt_nm='Visible Deposit',
        )
        option = FinancialProductOption.objects.create(
            product=product,
            save_trm=12,
            intr_rate='3.0000',
            intr_rate2='3.5000',
        )
        UserFinancialProduct.objects.create(user=other, option=option)

        response = self.client.get(f'/api/v1/profiles/{other.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('email', response.data)
        self.assertTrue(response.data['can_view_joined_products'])
        self.assertEqual(len(response.data['joined_products']), 1)
        self.assertEqual(response.data['joined_products'][0]['option']['id'], option.id)
