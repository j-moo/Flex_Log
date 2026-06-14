from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Friend
from .serializers import FriendRequestSerializer, FriendSerializer, SimpleUserSerializer
User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search(request):
    keyword = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)
    if keyword:
        users = users.filter(Q(username__icontains=keyword) | Q(email__icontains=keyword))
    return Response(SimpleUserSerializer(users[:20], many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_friend(request):
    serializer = FriendRequestSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    target = User.objects.get(id=serializer.validated_data['friend_id'])
    existing = Friend.objects.filter(Q(user=request.user, friend=target) | Q(user=target, friend=request.user)).first()
    if existing:
        return Response({'detail': '이미 친구 요청 또는 친구 관계가 존재합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    friend = Friend.objects.create(user=request.user, friend=target)
    return Response(FriendSerializer(friend).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def received_requests(request):
    qs = Friend.objects.filter(friend=request.user, status=Friend.PENDING).select_related('user', 'friend')
    return Response(FriendSerializer(qs, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_list(request):
    qs = Friend.objects.filter(Q(user=request.user) | Q(friend=request.user), status=Friend.ACCEPTED).select_related('user', 'friend')
    result = []
    for row in qs:
        other = row.friend if row.user == request.user else row.user
        result.append(SimpleUserSerializer(other).data)
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_request(request, friend_id):
    try:
        friend = Friend.objects.get(id=friend_id, friend=request.user, status=Friend.PENDING)
    except Friend.DoesNotExist:
        return Response({'detail': '처리할 친구 요청이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    action = request.data.get('action')
    if action == 'accept':
        friend.status = Friend.ACCEPTED
    elif action == 'reject':
        friend.status = Friend.REJECTED
    else:
        return Response({'detail': 'action은 accept 또는 reject여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    friend.save()
    return Response(FriendSerializer(friend).data)
