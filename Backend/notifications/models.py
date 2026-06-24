from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class Type(models.TextChoices):
        LIKE = 'like', '좋아요'
        COMMENT = 'comment', '댓글'
        AI_ANALYSIS = 'ai_analysis', 'AI분석'
        FRIEND_REQUEST = 'friend_request', '친구요청'
        STOCK_MOVEMENT = 'stock_movement', '주가변동'
        PRODUCT_RECOMMENDATION = 'product_recommendation', '상품추천'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=32, choices=Type.choices)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    target_route = models.CharField(max_length=80, blank=True)
    target_params = models.JSONField(default=dict, blank=True)
    target_query = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=160, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('user', 'is_read', '-created_at'), name='notification_user_read_idx'),
            models.Index(fields=('user', 'dedupe_key'), name='notification_user_dedupe_idx'),
        ]

    def mark_read(self):
        if self.is_read:
            return
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=('is_read', 'read_at'))

    def __str__(self):
        return f'{self.user} - {self.title}'
