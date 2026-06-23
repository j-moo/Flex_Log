from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


def default_expiration():
    return timezone.now() + timedelta(hours=24)


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class ExpenseLog(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', '전체 공개'
        FRIENDS = 'friends', '친구 공개'
        PRIVATE = 'private', '나만 보기'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_logs',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='expense_logs',
    )
    title = models.CharField(max_length=150, blank=True, default='')
    media = models.FileField(upload_to='expenses/%Y/%m/', blank=True, null=True)
    media_data = models.BinaryField(blank=True, null=True)
    media_content_type = models.CharField(max_length=120, blank=True)
    media_name = models.CharField(max_length=255, blank=True)
    amount = models.PositiveBigIntegerField()
    product_name = models.CharField(max_length=100, blank=True)
    merchant = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)
    overlay_text = models.CharField(max_length=120, blank=True)
    overlay_style = models.JSONField(default=dict, blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.FRIENDS,
    )
    hide_amount = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=default_expiration)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('user', '-created_at')),
            models.Index(fields=('category', '-created_at')),
            models.Index(fields=('visibility', 'is_visible', '-created_at')),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='expense_log_amount_positive',
            ),
            models.CheckConstraint(
                condition=Q(visibility__in=['public', 'friends', 'private']),
                name='expense_log_valid_visibility',
            ),
        ]

    @property
    def is_feed_visible(self):
        return self.is_visible and self.visibility != self.Visibility.PRIVATE

    def __str__(self):
        return f'{self.user} - {self.amount:,}원'


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_likes',
    )
    log = models.ForeignKey(
        ExpenseLog,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'log'),
                name='expense_like_unique_user_log',
            ),
        ]

    def __str__(self):
        return f'{self.user} likes expense #{self.log_id}'


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_comments',
    )
    log = models.ForeignKey(
        ExpenseLog,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.user} on expense #{self.log_id}'
