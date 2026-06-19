from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q


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

    save_trm = models.CharField(max_length=20, blank=True)

    intr_rate = models.FloatField(null=True, blank=True)
    intr_rate2 = models.FloatField(null=True, blank=True)

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

    title = models.CharField(max_length=100)
    description = models.TextField()
    reason = models.TextField()
    action_text = models.CharField(max_length=100, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(max_length=200, blank=True)
    product_type = models.CharField(max_length=20, blank=True)
    save_trm = models.CharField(max_length=20, blank=True)
    interest_rate = models.FloatField(null=True, blank=True)
    max_interest_rate = models.FloatField(null=True, blank=True)

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
