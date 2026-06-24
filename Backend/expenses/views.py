import re

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from friends.models import Friend
from notifications.helpers import upsert_grouped_notification
from notifications.models import Notification

from .models import Category, Comment, ExpenseLog, Like
from .serializers import CategorySerializer, CommentSerializer, ExpenseLogSerializer


EXPENSE_DELETE_CONFIRM_TEXT = (
    '정말 삭제하시겠습니까? 이거 삭제하면 로그 날아감 지인짜로오. '
    'AI 분석이랑 소비 통계에도 영향을 끼칩니다. 삭제된 피드는 복구할 수 없고, '
    '월별 소비 분석과 추천 결과도 달라질 수 있습니다.'
)
DELETE_CONFIRM_CODE_PATTERN = re.compile(r'^\d{4}$')


def normalize_delete_confirmation_text(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def validate_delete_confirmation(data):
    code = str(data.get('confirmation_code', ''))
    text = normalize_delete_confirmation_text(data.get('confirmation_text', ''))
    expected = f'{EXPENSE_DELETE_CONFIRM_TEXT} 확인코드: {code}'
    return bool(
        DELETE_CONFIRM_CODE_PATTERN.fullmatch(code)
        and text == normalize_delete_confirmation_text(expected)
    )


def username_label(user):
    return f'@{user.username}'


def grouped_reaction_message(first_user, count, action):
    label = username_label(first_user)
    if count <= 1:
        return f'{label}님이 내 피드에 {action}.'
    return f'{label}님 외 {count - 1}명이 내 피드에 {action}.'


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
            Q(user=self.request.user, is_visible=True)
            | Q(
                user_id__in=friend_ids,
                is_visible=True,
                visibility__in=[ExpenseLog.Visibility.PUBLIC, ExpenseLog.Visibility.FRIENDS],
            )
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        raw_limit = request.query_params.get('limit')
        raw_offset = request.query_params.get('offset')
        if raw_limit is None and raw_offset is None:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        try:
            limit = int(raw_limit or 10)
            offset = int(raw_offset or 0)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'limit과 offset은 숫자여야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = min(max(limit, 1), 30)
        offset = max(offset, 0)
        count = queryset.count()
        serializer = self.get_serializer(queryset[offset:offset + limit], many=True)
        next_offset = offset + limit if offset + limit < count else None
        return Response({
            'count': count,
            'next_offset': next_offset,
            'results': serializer.data,
        })


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
        else:
            likers = log.likes.exclude(user=log.user).select_related('user').order_by('created_at')
            first_like = likers.first()
            if first_like:
                liker_count = likers.count()
                upsert_grouped_notification(
                    user=log.user,
                    actor=first_like.user,
                    notification_type=Notification.Type.LIKE,
                    title=f'좋아요 {liker_count}명',
                    message=grouped_reaction_message(first_like.user, liker_count, '좋아요를 눌렀습니다'),
                    target_route='log-detail',
                    target_params={'id': log.id},
                    dedupe_key=f'like:{log.id}',
                )

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
        log = self.get_log()
        serializer.save(user=self.request.user, log=log)
        comments = log.comments.exclude(user=log.user).select_related('user').order_by('created_at')
        first_comment = comments.first()
        if first_comment:
            commenter_count = comments.values('user_id').distinct().count()
            upsert_grouped_notification(
                user=log.user,
                actor=first_comment.user,
                notification_type=Notification.Type.COMMENT,
                title=f'댓글 {commenter_count}명',
                message=grouped_reaction_message(first_comment.user, commenter_count, '댓글을 남겼습니다'),
                target_route='log-detail',
                target_params={'id': log.id},
                dedupe_key=f'comment:{log.id}',
            )


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
