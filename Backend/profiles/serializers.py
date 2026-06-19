from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from friends.models import Friend

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(
        source='user.name',
        required=False,
        allow_blank=True,
        max_length=50,
    )
    friend_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'user_id',
            'username',
            'email',
            'name',
            'nickname',
            'image',
            'bio',
            'friend_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user_id',
            'username',
            'email',
            'friend_count',
            'created_at',
            'updated_at',
        )

    def get_friend_count(self, obj):
        return Friend.objects.filter(
            Q(user=obj.user) | Q(friend=obj.user),
            status=Friend.Status.ACCEPTED,
        ).count()

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save(update_fields=('name', 'updated_at'))
        return super().update(instance, validated_data)
