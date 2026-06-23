from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from profiles.models import Profile

from .serializers import SignUpSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        user = serializer.save()
        Profile.objects.create(user=user, nickname=user.username)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            'message': '회원가입이 완료되었습니다.',
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_value = request.data.get('refresh')
    if not refresh_value:
        return Response(
            {'refresh': ['refresh 토큰이 필요합니다.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        RefreshToken(refresh_value).blacklist()
    except TokenError:
        return Response(
            {'refresh': ['유효하지 않거나 이미 폐기된 토큰입니다.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)
