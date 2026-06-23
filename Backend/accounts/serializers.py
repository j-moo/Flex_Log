from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'password', 'password_confirm')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'validators': []},
            'name': {'required': False, 'allow_blank': True},
        }

    def validate_username(self, value):
        username = value.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError('이미 사용 중인 아이디입니다.')
        return username

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})

        user = User(
            username=attrs['username'],
            email=attrs['email'],
            name=attrs.get('name', ''),
        )
        try:
            validate_password(attrs['password'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'profile_image')
        read_only_fields = fields

    def get_profile_image(self, obj):
        profile = getattr(obj, 'profile', None)
        image = getattr(profile, 'image', None)
        if not image:
            return None
        try:
            if image.name and not image.storage.exists(image.name):
                return None
            url = image.url
        except (OSError, ValueError):
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url
