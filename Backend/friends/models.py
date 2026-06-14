from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

class Friend(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [(PENDING, '대기'), (ACCEPTED, '수락'), (REJECTED, '거절')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_friend_requests')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'friend'], name='unique_friend_direction')]

    def clean(self):
        if self.user_id == self.friend_id:
            raise ValidationError('자기 자신에게 친구 요청을 보낼 수 없습니다.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

def are_friends(user_a, user_b):
    if not user_a.is_authenticated or not user_b.is_authenticated:
        return False
    return Friend.objects.filter(Q(user=user_a, friend=user_b) | Q(user=user_b, friend=user_a), status=Friend.ACCEPTED).exists()
