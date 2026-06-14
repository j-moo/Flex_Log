from rest_framework import serializers
from .models import Category, Comment, ExpenseLog

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'created_at')

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Comment
        fields = ('id', 'user', 'username', 'log', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'username', 'log', 'created_at', 'updated_at')

class ExpenseLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_active_story = serializers.BooleanField(read_only=True)
    class Meta:
        model = ExpenseLog
        fields = ('id','user','username','category','category_name','media','amount','content','created_at','updated_at','expires_at','is_visible','is_active_story','like_count','comment_count','is_liked')
        read_only_fields = ('id','user','username','created_at','updated_at','expires_at')
    def get_is_liked(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.likes.filter(user=request.user).exists())

class ExpenseLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseLog
        fields = ('id','category','media','amount','content')
    def validate_amount(self, value):
        if value <= 0: raise serializers.ValidationError('소비 금액은 0보다 커야 합니다.')
        return value
