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
    media = models.FileField(upload_to='expenses/%Y/%m/', blank=True, null=True)
    amount = models.PositiveBigIntegerField()
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=default_expiration)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('user', '-created_at')),
            models.Index(fields=('category', '-created_at')),
            models.Index(fields=('is_visible', 'expires_at')),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='expense_log_amount_positive',
            ),
        ]

    @property
    def is_feed_visible(self):
        return self.is_visible and self.expires_at > timezone.now()

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

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    log = models.ForeignKey(
        ExpenseLog,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'log'),
                name='unique_user_log_like',
            )
        ]


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
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