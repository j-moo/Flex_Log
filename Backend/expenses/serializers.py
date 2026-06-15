from pathlib import Path

from rest_framework import serializers

from .models import Category, ExpenseLog


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = fields


class ExpenseLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_feed_visible = serializers.BooleanField(read_only=True)

    class Meta:
        model = ExpenseLog
        fields = (
            'id',
            'username',
            'category',
            'category_name',
            'media',
            'amount',
            'content',
            'expires_at',
            'is_visible',
            'is_feed_visible',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'username',
            'category_name',
            'is_feed_visible',
            'expires_at',
            'created_at',
            'updated_at',
        )

    def validate_media(self, value):
        if not value:
            return value
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('미디어 파일은 10MB 이하만 업로드할 수 있습니다.')
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}
        if Path(value.name).suffix.lower() not in allowed_extensions:
            raise serializers.ValidationError('지원하지 않는 미디어 형식입니다.')
        return value
