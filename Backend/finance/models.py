from django.conf import settings
from django.db import models
from analysis.models import AIAnalysis

class FinancialProduct(models.Model):
    DEPOSIT='deposit'; SAVING='saving'
    PRODUCT_TYPE_CHOICES=[(DEPOSIT,'예금'),(SAVING,'적금')]
    product_code = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    base_rate = models.FloatField(default=0)
    max_rate = models.FloatField(default=0)
    save_term = models.PositiveIntegerField(default=12)
    join_way = models.TextField(blank=True)
    special_condition = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ('-max_rate','bank_name')

class ProductRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_recommendations')
    ai_analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE, related_name='product_recommendations')
    product = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE, related_name='recommendations')
    reason = models.TextField()
    priority = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ('priority','-created_at')
