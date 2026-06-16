from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Friend
from .serializers import (
    FriendCreateSerializer,
    FriendSerializer,
    FriendStatusSerializer,
    FriendUserSerializer,
)


User = get_user_model()


class UserSearchView(generics.ListAPIView):
    serializer_class = FriendUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = User.objects.exclude(pk=self.request.user.pk).order_by('username')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(name__icontains=search)
                | Q(email__icontains=search)
            )
        return queryset[:20]


class FriendListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Friend.objects.filter(Q(user=self.request.user) | Q(friend=self.request.user))
            .select_related('user', 'friend')
            .order_by('-updated_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FriendCreateSerializer
        return FriendSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend = serializer.save()
        output = FriendSerializer(friend, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class FriendDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        return generics.get_object_or_404(
            Friend.objects.select_related('user', 'friend').filter(
                Q(user=request.user) | Q(friend=request.user)
            ),
            pk=pk,
        )

    def patch(self, request, pk):
        friend = self.get_object(request, pk)
        if friend.friend_id != request.user.id:
            return Response(
                {'detail': '친구 요청을 받은 사용자만 상태를 변경할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FriendStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend.status = serializer.validated_data['status']
        friend.save(update_fields=('status', 'updated_at'))
        return Response(FriendSerializer(friend, context={'request': request}).data)

    def delete(self, request, pk):
        friend = self.get_object(request, pk)
        friend.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
