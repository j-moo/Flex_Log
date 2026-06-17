from pathlib import Path

from rest_framework import serializers

from .models import Category, Comment, ExpenseLog


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = fields


class ExpenseLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_feed_visible = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseLog
        fields = (
            'id',
            'username',
            'display_name',
            'category',
            'category_name',
            'media',
            'amount',
            'content',
            'expires_at',
            'is_visible',
            'is_feed_visible',
            'like_count',
            'comment_count',
            'is_liked',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'username',
            'display_name',
            'category_name',
            'is_feed_visible',
            'like_count',
            'comment_count',
            'is_liked',
            'expires_at',
            'created_at',
            'updated_at',
        )

    def get_display_name(self, obj):
        return obj.user.name or obj.user.username

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def validate_media(self, value):
        if not value:
            return value
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('미디어 파일은 10MB 이하만 업로드할 수 있습니다.')
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}
        if Path(value.name).suffix.lower() not in allowed_extensions:
            raise serializers.ValidationError('지원하지 않는 미디어 형식입니다.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'log', 'username', 'display_name', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'log', 'username', 'display_name', 'created_at', 'updated_at')

    def get_display_name(self, obj):
        return obj.user.name or obj.user.username
