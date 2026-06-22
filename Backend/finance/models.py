from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class FinancialProduct(models.Model):
    PRODUCT_TYPES = (
        ('deposit', '정기예금'),
        ('saving', '정기적금'),
    )

    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    fin_prdt_cd = models.CharField(max_length=100)
    dcls_month = models.CharField(max_length=20, blank=True)

    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=200)

    join_way = models.TextField(blank=True)
    mtrt_int = models.TextField(blank=True)
    spcl_cnd = models.TextField(blank=True)
    join_deny = models.CharField(max_length=20, blank=True)
    join_member = models.TextField(blank=True)
    etc_note = models.TextField(blank=True)

    max_limit = models.BigIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    fetched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('product_type', 'kor_co_nm', 'fin_prdt_nm')
        constraints = [
            models.UniqueConstraint(
                fields=('product_type', 'fin_prdt_cd'),
                name='financial_product_unique_type_code',
            ),
        ]
        indexes = [
            models.Index(
                fields=('product_type', 'kor_co_nm'),
                name='finance_product_type_bank_idx',
            ),
            models.Index(fields=('fin_prdt_cd',), name='finance_product_code_idx'),
        ]

    def __str__(self):
        return f'{self.kor_co_nm} - {self.fin_prdt_nm}'


class FinancialProductOption(models.Model):
    product = models.ForeignKey(
        FinancialProduct,
        on_delete=models.CASCADE,
        related_name='options',
    )

    intr_rate_type = models.CharField(max_length=20, blank=True)
    intr_rate_type_nm = models.CharField(max_length=50, blank=True)

    save_trm = models.PositiveSmallIntegerField()

    intr_rate = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    intr_rate2 = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)

    rsrv_type = models.CharField(max_length=20, blank=True)
    rsrv_type_nm = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('product', 'save_trm', 'intr_rate_type', 'rsrv_type')
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'save_trm', 'intr_rate_type', 'rsrv_type'),
                name='financial_option_unique_product_terms',
            ),
            models.CheckConstraint(
                condition=Q(save_trm__gt=0),
                name='financial_option_term_positive',
            ),
            models.CheckConstraint(
                condition=Q(intr_rate__isnull=True) | Q(intr_rate__gte=0),
                name='financial_option_rate_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(intr_rate2__isnull=True) | Q(intr_rate2__gte=0),
                name='financial_option_max_rate_nonnegative',
            ),
        ]
        indexes = [
            models.Index(fields=('save_trm',), name='finance_option_term_idx'),
            models.Index(fields=('intr_rate2',), name='finance_option_rate2_idx'),
        ]

    def __str__(self):
        return f'{self.product.fin_prdt_nm} - {self.save_trm} months'


class FinancialProductRecommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_product_recommendations',
    )
    analysis = models.ForeignKey(
        'analysis.MonthlyAIAnalysis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_product_recommendations',
    )
    product = models.ForeignKey(
        FinancialProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_product_recommendations',
    )
    option = models.ForeignKey(
        FinancialProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_product_recommendations',
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    reason = models.TextField()
    action_text = models.CharField(max_length=100, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(max_length=200, blank=True)
    product_type = models.CharField(max_length=20, blank=True)
    save_trm = models.PositiveSmallIntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    max_interest_rate = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)

    ai_comment = models.TextField(blank=True)
    caution = models.TextField(blank=True)

    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('priority', '-created_at')
        indexes = [
            models.Index(fields=('user', '-created_at'), name='finance_reco_user_created_idx'),
            models.Index(fields=('priority', '-created_at'), name='finance_reco_priority_idx'),
        ]

    def __str__(self):
        return f'{self.user} - {self.title}'


class UserFinancialProduct(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', '가입 중'
        CANCELLED = 'cancelled', '해지'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='joined_financial_products',
    )
    option = models.ForeignKey(
        FinancialProductOption,
        on_delete=models.PROTECT,
        related_name='user_subscriptions',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    joined_at = models.DateTimeField(default=timezone.now)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-joined_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'option'),
                name='user_financial_product_unique_user_option',
            ),
            models.CheckConstraint(
                condition=Q(status__in=['active', 'cancelled']),
                name='user_financial_product_valid_status',
            ),
            models.CheckConstraint(
                condition=(
                    Q(status='active', cancelled_at__isnull=True)
                    | Q(status='cancelled', cancelled_at__isnull=False)
                ),
                name='user_financial_product_status_date_consistent',
            ),
        ]
        indexes = [
            models.Index(fields=('user', 'status'), name='user_fin_product_status_idx'),
        ]

    def clean(self):
        if self.status == self.Status.ACTIVE and self.cancelled_at is not None:
            raise ValidationError({'cancelled_at': '가입 중인 상품에는 해지 시각을 지정할 수 없습니다.'})
        if self.status == self.Status.CANCELLED and self.cancelled_at is None:
            raise ValidationError({'cancelled_at': '해지된 상품에는 해지 시각이 필요합니다.'})

    def __str__(self):
        return f'{self.user} - {self.option}'


class Commodity(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=30)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('code',)
        constraints = [
            models.CheckConstraint(
                condition=Q(code__in=['GOLD', 'SILVER']),
                name='commodity_valid_code',
            ),
        ]

    def __str__(self):
        return self.name


class CommodityPrice(models.Model):
    commodity = models.ForeignKey(
        Commodity,
        on_delete=models.CASCADE,
        related_name='prices',
    )
    price_date = models.DateField()
    close_price = models.DecimalField(max_digits=18, decimal_places=6)
    open_price = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    high_price = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    low_price = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('price_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('commodity', 'price_date'),
                name='commodity_price_unique_asset_date',
            ),
            models.CheckConstraint(
                condition=Q(close_price__gte=0),
                name='commodity_price_close_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(open_price__isnull=True) | Q(open_price__gte=0),
                name='commodity_price_open_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(high_price__isnull=True) | Q(high_price__gte=0),
                name='commodity_price_high_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(low_price__isnull=True) | Q(low_price__gte=0),
                name='commodity_price_low_nonnegative',
            ),
        ]
        indexes = [
            models.Index(fields=('commodity', 'price_date'), name='commodity_asset_date_idx'),
        ]

    def __str__(self):
        return f'{self.commodity.code} - {self.price_date}'


class StockHolding(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stock_holdings',
    )
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    average_price = models.DecimalField(max_digits=18, decimal_places=2)
    current_price = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0'))
    memo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('symbol',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'symbol'),
                name='stock_holding_unique_user_symbol',
            ),
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name='stock_holding_quantity_positive',
            ),
            models.CheckConstraint(
                condition=Q(average_price__gte=0),
                name='stock_holding_average_price_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(current_price__gte=0),
                name='stock_holding_current_price_nonnegative',
            ),
        ]
        indexes = [
            models.Index(fields=('user', 'symbol'), name='stock_holding_user_symbol_idx'),
        ]

    @property
    def invested_amount(self):
        return self.quantity * self.average_price

    @property
    def valuation_amount(self):
        return self.quantity * self.current_price

    @property
    def profit_loss(self):
        return self.valuation_amount - self.invested_amount

    @property
    def profit_rate(self):
        if not self.invested_amount:
            return Decimal('0')
        return (self.profit_loss / self.invested_amount) * Decimal('100')

    def __str__(self):
        return f'{self.user} - {self.symbol}'
