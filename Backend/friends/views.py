from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Friend
from .serializers import (
    FriendSerializer,
    FriendStatusUpdateSerializer,
    UserSearchSerializer,
)

User = get_user_model()


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = self.request.query_params.get('q', '')

        queryset = User.objects.exclude(id=self.request.user.id)

        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )

        return queryset[:20]


class FriendListCreateView(generics.ListCreateAPIView):
    serializer_class = FriendSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Friend.objects.filter(
            Q(user=self.request.user) |
            Q(friend=self.request.user)
        ).select_related('user', 'friend')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FriendUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendStatusUpdateSerializer
    queryset = Friend.objects.all()

    def get_queryset(self):
        return Friend.objects.filter(friend=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            FriendSerializer(instance).data,
            status=status.HTTP_200_OK,
        )