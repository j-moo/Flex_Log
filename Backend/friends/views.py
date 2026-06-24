from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.helpers import create_notification, get_display_name
from notifications.models import Notification

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
        if self.request.query_params.get('recommend') in {'1', 'true', 'True'}:
            return self.get_recommendations()

        queryset = (
            User.objects.exclude(pk=self.request.user.pk)
            .select_related('profile')
            .order_by('username')
        )
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(name__icontains=search)
                | Q(profile__nickname__icontains=search)
            )
        return queryset[:20]

    def get_recommendations(self):
        user = self.request.user
        accepted_relations = Friend.objects.filter(
            Q(user=user) | Q(friend=user),
            status=Friend.Status.ACCEPTED,
        )
        friend_ids = {
            relation.friend_id if relation.user_id == user.id else relation.user_id
            for relation in accepted_relations
        }
        if not friend_ids:
            return []

        existing_relation_ids = set(friend_ids)
        all_relations = Friend.objects.filter(Q(user=user) | Q(friend=user))
        for relation in all_relations:
            existing_relation_ids.add(
                relation.friend_id if relation.user_id == user.id else relation.user_id
            )

        mutuals_by_user = {}
        friend_network = (
            Friend.objects.filter(
                Q(user_id__in=friend_ids) | Q(friend_id__in=friend_ids),
                status=Friend.Status.ACCEPTED,
            )
            .exclude(Q(user=user) | Q(friend=user))
        )
        for relation in friend_network:
            if relation.user_id in friend_ids:
                candidate_id = relation.friend_id
                mutual_id = relation.user_id
            else:
                candidate_id = relation.user_id
                mutual_id = relation.friend_id

            if candidate_id == user.id or candidate_id in existing_relation_ids:
                continue
            mutuals_by_user.setdefault(candidate_id, set()).add(mutual_id)

        if not mutuals_by_user:
            return []

        users = list(
            User.objects.filter(id__in=mutuals_by_user.keys())
            .select_related('profile')
        )
        for candidate in users:
            candidate.mutual_friend_count = len(mutuals_by_user.get(candidate.id, ()))

        users.sort(key=lambda item: (-item.mutual_friend_count, item.username))
        return users[:20]


class FriendListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Friend.objects.filter(Q(user=self.request.user) | Q(friend=self.request.user))
            .select_related('user', 'user__profile', 'friend', 'friend__profile')
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
        create_notification(
            user=friend.friend,
            actor=friend.user,
            notification_type=Notification.Type.FRIEND_REQUEST,
            title='친구 요청',
            message=f'{get_display_name(friend.user)}님이 친구 요청을 보냈습니다.',
            target_route='friends',
            dedupe_key=f'friend-request:{friend.id}',
        )
        output = FriendSerializer(friend, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class FriendDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        return generics.get_object_or_404(
            Friend.objects.select_related('user', 'user__profile', 'friend', 'friend__profile').filter(
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
