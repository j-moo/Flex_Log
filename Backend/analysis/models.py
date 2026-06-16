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


class MonthlyAIAnalysis(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'low', '낮음'
        MEDIUM = 'medium', '보통'
        HIGH = 'high', '높음'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monthly_ai_analyses',
    )
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    total_amount = models.PositiveBigIntegerField(default=0)
    log_count = models.PositiveIntegerField(default=0)
    average_amount = models.PositiveBigIntegerField(default=0)
    category_summary = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    saving_tip = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('user', '-created_at')),
            models.Index(fields=('user', 'year', 'month')),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(month__gte=1, month__lte=12),
                name='monthly_ai_analysis_valid_month',
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name='monthly_ai_analysis_total_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(log_count__gte=0),
                name='monthly_ai_analysis_log_count_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(average_amount__gte=0),
                name='monthly_ai_analysis_average_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(risk_level__in=['low', 'medium', 'high']),
                name='monthly_ai_analysis_valid_risk_level',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.year}-{self.month:02d} ({self.risk_level})'
