from django.conf import settings
from django.db import models
from django.db.models import Q


class FinancialProduct(models.Model):
    class ProductType(models.TextChoices):
        DEPOSIT = 'deposit', '예금'
        SAVING = 'saving', '적금'

    product_code = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=10, choices=ProductType.choices)
    base_rate = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    max_rate = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    save_term = models.PositiveSmallIntegerField(help_text='가입 기간(개월)')
    join_way = models.TextField(blank=True)
    special_condition = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('bank_name', 'product_name')
        constraints = [
            models.CheckConstraint(
                condition=Q(product_type__in=['deposit', 'saving']),
                name='financial_product_valid_type',
            ),
            models.CheckConstraint(
                condition=Q(base_rate__gte=0),
                name='financial_product_base_rate_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(max_rate__gte=0),
                name='financial_product_max_rate_nonnegative',
            ),
        ]

    def __str__(self):
        return f'{self.bank_name} - {self.product_name}'


class ProductRecommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_recommendations',
    )
    ai_analysis = models.ForeignKey(
        'analysis.AIAnalysis',
        on_delete=models.CASCADE,
        related_name='product_recommendations',
    )
    product = models.ForeignKey(
        FinancialProduct,
        on_delete=models.CASCADE,
        related_name='recommendations',
    )
    reason = models.TextField()
    priority = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('priority', '-created_at')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'ai_analysis', 'product'),
                name='product_recommendation_unique_result',
            ),
            models.CheckConstraint(
                condition=Q(priority__gt=0),
                name='product_recommendation_priority_positive',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.product}'


class StockHolding(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stock_holdings',
    )
    stock_symbol = models.CharField(max_length=20)
    stock_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    average_price = models.DecimalField(max_digits=18, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('stock_symbol',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'stock_symbol'),
                name='stock_holding_unique_user_symbol',
            ),
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name='stock_holding_quantity_positive',
            ),
            models.CheckConstraint(
                condition=Q(average_price__gt=0),
                name='stock_holding_average_price_positive',
            ),
        ]

    def save(self, *args, **kwargs):
        self.stock_symbol = self.stock_symbol.strip().upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.stock_symbol}'
