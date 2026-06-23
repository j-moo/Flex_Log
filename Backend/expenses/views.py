import re

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from friends.models import Friend

from .models import Category, Comment, ExpenseLog, Like
from .serializers import CategorySerializer, CommentSerializer, ExpenseLogSerializer


EXPENSE_DELETE_CONFIRM_TEXT = (
    '정말 삭제하시겠습니까? 이거 삭제하면 로그 날아감 지인짜로오. '
    'AI 분석이랑 소비 통계에도 영향을 끼칩니다. 삭제된 피드는 복구할 수 없고, '
    '월별 소비 분석과 추천 결과도 달라질 수 있습니다.'
)
DELETE_CONFIRM_CODE_PATTERN = re.compile(r'^\d{4}$')


def validate_delete_confirmation(data):
    code = str(data.get('confirmation_code', ''))
    text = str(data.get('confirmation_text', ''))
    expected = f'{EXPENSE_DELETE_CONFIRM_TEXT} 확인코드: {code}'
    return bool(DELETE_CONFIRM_CODE_PATTERN.fullmatch(code) and text == expected)


def accepted_friend_ids(user):
    sent_ids = Friend.objects.filter(
        user=user,
        status=Friend.Status.ACCEPTED,
    ).values_list('friend_id', flat=True)
    received_ids = Friend.objects.filter(
        friend=user,
        status=Friend.Status.ACCEPTED,
    ).values_list('user_id', flat=True)
    return set(sent_ids).union(received_ids)


def base_log_queryset():
    return (
        ExpenseLog.objects.select_related('user', 'user__profile', 'category')
        .prefetch_related('likes', 'comments')
        .order_by('-created_at')
    )


def accessible_log_queryset(user):
    friend_ids = accepted_friend_ids(user)
    return base_log_queryset().filter(
        Q(user=user)
        | Q(is_visible=True, visibility=ExpenseLog.Visibility.PUBLIC)
        | Q(
            user_id__in=friend_ids,
            is_visible=True,
            visibility__in=[ExpenseLog.Visibility.PUBLIC, ExpenseLog.Visibility.FRIENDS],
        )
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
        return base_log_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        if self.request.method in {'PATCH', 'PUT', 'DELETE'}:
            # 수정/삭제는 소비 통계와 AI 분석 원본 데이터에 영향을 주므로 작성자 본인 로그로 제한한다.
            return base_log_queryset().filter(user=self.request.user)
        return accessible_log_queryset(self.request.user)

    def destroy(self, request, *args, **kwargs):
        # 프론트 확인 모달을 우회한 DELETE 요청도 서버에서 한 번 더 차단한다.
        if not validate_delete_confirmation(request.data):
            return Response(
                {'detail': '삭제 확인 문구가 일치하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class FriendFeedListView(generics.ListAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        friend_ids = accepted_friend_ids(self.request.user)
        return base_log_queryset().filter(
            user_id__in=friend_ids,
            is_visible=True,
            visibility__in=[ExpenseLog.Visibility.PUBLIC, ExpenseLog.Visibility.FRIENDS],
        )


class UserExpenseLogListView(generics.ListAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        if user_id == self.request.user.id:
            return base_log_queryset().filter(user_id=user_id)
        return accessible_log_queryset(self.request.user).filter(user_id=user_id)


class LikeToggleView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        log = generics.get_object_or_404(accessible_log_queryset(request.user), pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, log=log)
        if not created:
            like.delete()

        log.refresh_from_db()
        return Response(
            {
                'liked': created,
                'like_count': log.likes.count(),
            },
            status=status.HTTP_200_OK,
        )


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_log(self):
        return generics.get_object_or_404(
            accessible_log_queryset(self.request.user),
            pk=self.kwargs['pk'],
        )

    def get_queryset(self):
        return Comment.objects.filter(log=self.get_log()).select_related('user', 'user__profile', 'log')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, log=self.get_log())


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).select_related('user', 'user__profile', 'log')

    def get_object(self):
        log = generics.get_object_or_404(
            accessible_log_queryset(self.request.user),
            pk=self.kwargs['pk'],
        )
        return generics.get_object_or_404(
            self.get_queryset(),
            log=log,
            pk=self.kwargs['comment_pk'],
        )
