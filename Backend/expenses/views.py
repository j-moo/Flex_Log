from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Comment, ExpenseLog, Like
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    ExpenseLogSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class ExpenseLogListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        return (
            ExpenseLog.objects
            .filter(user=self.request.user)
            .select_related('user', 'category')
            .annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True),
            )
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ExpenseLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        return (
            ExpenseLog.objects
            .filter(user=self.request.user)
            .select_related('user', 'category')
            .annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True),
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FriendExpenseFeedView(generics.ListAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        from friends.models import Friend

        accepted_friends = Friend.objects.filter(
            Q(user=self.request.user) | Q(friend=self.request.user),
            status='accepted',
        )

        friend_ids = []

        for relation in accepted_friends:
            if relation.user_id == self.request.user.id:
                friend_ids.append(relation.friend_id)
            else:
                friend_ids.append(relation.user_id)

        return (
            ExpenseLog.objects
            .filter(
                user_id__in=friend_ids,
                is_visible=True,
            )
            .select_related('user', 'category')
            .annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True),
            )
            .order_by('-created_at')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ExpenseLikeToggleView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        log = get_object_or_404(ExpenseLog, pk=pk)

        like, created = Like.objects.get_or_create(
            user=request.user,
            log=log,
        )

        if not created:
            like.delete()
            return Response({'liked': False})

        return Response({'liked': True})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Comment.objects
            .filter(log_id=self.kwargs['pk'])
            .select_related('user')
        )

    def perform_create(self, serializer):
        log = get_object_or_404(
            ExpenseLog,
            pk=self.kwargs['pk'],
        )

        serializer.save(
            user=self.request.user,
            log=log,
        )


class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)