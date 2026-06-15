from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Friend(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        ACCEPTED = 'accepted', '수락'
        REJECTED = 'rejected', '거절'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.CheckConstraint(
                condition=~Q(user=F('friend')),
                name='friend_prevent_self_request',
            ),
            models.CheckConstraint(
                condition=Q(status__in=['pending', 'accepted', 'rejected']),
                name='friend_valid_status',
            ),
            models.UniqueConstraint(
                fields=('user', 'friend'),
                name='friend_unique_request_pair',
            ),
        ]

    def clean(self):
        if self.user_id == self.friend_id:
            raise ValidationError('자기 자신에게 친구 요청을 보낼 수 없습니다.')
        reverse_exists = Friend.objects.filter(
            user_id=self.friend_id,
            friend_id=self.user_id,
        ).exclude(pk=self.pk).exists()
        if reverse_exists:
            raise ValidationError('두 사용자 사이에는 하나의 친구 관계만 존재할 수 있습니다.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} -> {self.friend} ({self.status})'
