from django.conf import settings
from django.db import models

class MonthlyAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monthly_analyses')
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField(default=0)
    category_summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','year','month'], name='unique_user_year_month_analysis')]
        ordering = ('-year','-month')

class AIAnalysis(models.Model):
    SUCCESS='success'; FAILED='failed'; FALLBACK='fallback'
    STATUS_CHOICES=[(SUCCESS,'성공'),(FAILED,'실패'),(FALLBACK,'대체 피드백')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis = models.ForeignKey(MonthlyAnalysis, on_delete=models.CASCADE, related_name='ai_analyses')
    input_summary = models.TextField()
    result = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SUCCESS)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ('-created_at',)
