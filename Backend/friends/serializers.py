from django.contrib.auth import get_user_model
from rest_framework import serializers

from profiles.utils import get_profile_image_url

from .models import Friend


User = get_user_model()


class FriendUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    mutual_friend_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'display_name', 'profile_image', 'mutual_friend_count')
        read_only_fields = fields

    def get_display_name(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.nickname:
            return profile.nickname
        return obj.name or obj.username

    def get_profile_image(self, obj):
        profile = getattr(obj, 'profile', None)
        return get_profile_image_url(profile, self.context.get('request'))

    def get_mutual_friend_count(self, obj):
        return getattr(obj, 'mutual_friend_count', 0)


class FriendSerializer(serializers.ModelSerializer):
    user = FriendUserSerializer(read_only=True)
    friend = FriendUserSerializer(read_only=True)
    counterpart = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ('id', 'user', 'friend', 'counterpart', 'status', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_counterpart(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        counterpart = obj.friend if obj.user_id == request.user.id else obj.user
        return FriendUserSerializer(counterpart, context=self.context).data


class FriendCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ('friend',)

    def validate_friend(self, value):
        request = self.context['request']
        if value == request.user:
            raise serializers.ValidationError('자기 자신에게 친구 요청을 보낼 수 없습니다.')

        exists = Friend.objects.filter(user=request.user, friend=value).exists()
        reverse_exists = Friend.objects.filter(user=value, friend=request.user).exists()
        if exists or reverse_exists:
            raise serializers.ValidationError('이미 친구 요청 또는 친구 관계가 존재합니다.')
        return value

    def create(self, validated_data):
        return Friend.objects.create(user=self.context['request'].user, **validated_data)


class FriendStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(Friend.Status.ACCEPTED, Friend.Status.REJECTED))
