from django.db import transaction
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(
        source='user.name',
        required=False,
        allow_blank=True,
        max_length=50,
    )

    class Meta:
        model = Profile
        fields = (
            'id',
            'username',
            'email',
            'name',
            'nickname',
            'image',
            'bio',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'username', 'email', 'created_at', 'updated_at')

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save(update_fields=('name', 'updated_at'))
        return super().update(instance, validated_data)
