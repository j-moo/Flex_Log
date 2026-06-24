from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from friends.models import Friend
from finance.models import UserFinancialProduct
from finance.serializers import UserFinancialProductSerializer

from .models import Profile
from .utils import get_profile_image_url


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
    joined_products = serializers.SerializerMethodField()
    can_view_joined_products = serializers.SerializerMethodField()

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
            'joined_products',
            'can_view_joined_products',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user_id',
            'username',
            'email',
            'friend_count',
            'joined_products',
            'can_view_joined_products',
            'created_at',
            'updated_at',
        )

    def get_friend_count(self, obj):
        return Friend.objects.filter(
            Q(user=obj.user) | Q(friend=obj.user),
            status=Friend.Status.ACCEPTED,
        ).count()

    def get_joined_products(self, obj):
        if not self._can_view_joined_products(obj):
            return []

        subscriptions = getattr(obj.user, 'active_joined_products', None)
        if subscriptions is None:
            subscriptions = UserFinancialProduct.objects.filter(
                user=obj.user,
                status=UserFinancialProduct.Status.ACTIVE,
            ).select_related('option', 'option__product').prefetch_related(
                'option__product__options',
            )
        return UserFinancialProductSerializer(subscriptions, many=True).data

    def get_can_view_joined_products(self, obj):
        return self._can_view_joined_products(obj)

    def _can_view_joined_products(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if obj.user_id == user.id:
            return True
        return Friend.objects.filter(
            (
                Q(user=user, friend=obj.user)
                | Q(user=obj.user, friend=user)
            ),
            status=Friend.Status.ACCEPTED,
        ).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = get_profile_image_url(instance, self.context.get('request'))
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated or instance.user_id != user.id:
            data.pop('email', None)
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save(update_fields=('name', 'updated_at'))
        return super().update(instance, validated_data)
