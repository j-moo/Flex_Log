from django.conf import settings
from django.db import models
from django.db.models import Q


class MonthlyAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monthly_analyses',
    )
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    total_amount = models.PositiveBigIntegerField(default=0)
    category_summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-year', '-month')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'year', 'month'),
                name='monthly_analysis_unique_user_period',
            ),
            models.CheckConstraint(
                condition=Q(month__gte=1, month__lte=12),
                name='monthly_analysis_valid_month',
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name='monthly_analysis_total_nonnegative',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.year}-{self.month:02d}'


class AIAnalysis(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'success', '성공'
        FAILED = 'failed', '실패'
        FALLBACK = 'fallback', '대체 분석'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_analyses',
    )
    analysis = models.ForeignKey(
        MonthlyAnalysis,
        on_delete=models.CASCADE,
        related_name='ai_analyses',
    )
    input_summary = models.TextField()
    result = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=['success', 'failed', 'fallback']),
                name='ai_analysis_valid_status',
            ),
        ]

    def __str__(self):
        return f'{self.analysis} - {self.status}'
