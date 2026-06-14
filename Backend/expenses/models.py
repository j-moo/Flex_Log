from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone

def default_expire_time():
    return timezone.now() + timedelta(hours=24)

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class ExpenseLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_logs')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expense_logs')
    media = models.FileField(upload_to='expenses/', blank=True, null=True)
    amount = models.PositiveIntegerField()
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=default_expire_time)
    is_visible = models.BooleanField(default=True)
    class Meta: ordering = ('-created_at',)
    @property
    def is_active_story(self): return self.is_visible and self.expires_at > timezone.now()

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    log = models.ForeignKey(ExpenseLog, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'log'], name='unique_user_log_like')]

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    log = models.ForeignKey(ExpenseLog, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ('created_at',)
