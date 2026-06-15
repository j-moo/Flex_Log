from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Friend

User = get_user_model()


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class FriendSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    friend_username = serializers.CharField(source='friend.username', read_only=True)

    class Meta:
        model = Friend
        fields = (
            'id',
            'user',
            'user_username',
            'friend',
            'friend_username',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user',
            'user_username',
            'friend_username',
            'status',
            'created_at',
            'updated_at',
        )


class FriendStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ('status',)

    def validate_status(self, value):
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError('accepted 또는 rejected만 가능합니다.')
        return value