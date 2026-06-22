from pathlib import Path

from rest_framework import serializers

from .models import Category, Comment, ExpenseLog


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = fields


class ExpenseLogSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_feed_visible = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseLog
        fields = (
            'id',
            'user_id',
            'username',
            'display_name',
            'category',
            'category_name',
            'title',
            'media',
            'amount',
            'product_name',
            'merchant',
            'content',
            'overlay_text',
            'overlay_style',
            'visibility',
            'hide_amount',
            'expires_at',
            'is_visible',
            'is_feed_visible',
            'like_count',
            'comment_count',
            'is_liked',
            'can_edit',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user_id',
            'username',
            'display_name',
            'category_name',
            'is_feed_visible',
            'like_count',
            'comment_count',
            'is_liked',
            'can_edit',
            'expires_at',
            'created_at',
            'updated_at',
        )

    def get_display_name(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.nickname:
            return profile.nickname
        return obj.user.name or obj.user.username

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.user_id == request.user.id)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        is_owner = bool(request and request.user.is_authenticated and instance.user_id == request.user.id)
        if instance.hide_amount and not is_owner:
            data['amount'] = None
        return data

    def validate_media(self, value):
        if not value:
            return value
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('미디어 파일은 10MB 이하만 업로드할 수 있습니다.')
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}
        if Path(value.name).suffix.lower() not in allowed_extensions:
            raise serializers.ValidationError('지원하지 않는 미디어 형식입니다.')
        return value

    def validate_overlay_style(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('텍스트 스타일은 객체 형식이어야 합니다.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'log',
            'user_id',
            'username',
            'display_name',
            'content',
            'can_edit',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'log',
            'user_id',
            'username',
            'display_name',
            'can_edit',
            'created_at',
            'updated_at',
        )

    def get_display_name(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.nickname:
            return profile.nickname
        return obj.user.name or obj.user.username

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.user_id == request.user.id)
