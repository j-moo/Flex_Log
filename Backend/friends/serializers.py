from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Friend
User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname')
    def get_nickname(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.nickname if profile else obj.username

class FriendSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    friend = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Friend
        fields = ('id', 'user', 'friend', 'status', 'created_at', 'updated_at')

class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField()
    def validate_friend_id(self, value):
        request = self.context['request']
        if request.user.id == value:
            raise serializers.ValidationError('자기 자신에게 친구 요청을 보낼 수 없습니다.')
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError('존재하지 않는 사용자입니다.')
        return value
