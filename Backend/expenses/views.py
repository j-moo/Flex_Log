from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from friends.models import Friend, are_friends
from .models import Category, Comment, ExpenseLog, Like
from .serializers import CategorySerializer, CommentSerializer, ExpenseLogCreateSerializer, ExpenseLogSerializer

def can_view_log(user, log): return log.user_id == user.id or are_friends(user, log.user)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def categories(request):
    if request.method == 'GET':
        return Response(CategorySerializer(Category.objects.all().order_by('id'), many=True).data)
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(); return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seed_categories(request):
    for name in ['식비','교통비','문화생활','쇼핑','공과금','카페','구독','기타']:
        Category.objects.get_or_create(name=name)
    return Response({'message': '기본 카테고리가 생성되었습니다.'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def logs(request):
    if request.method == 'GET':
        qs = ExpenseLog.objects.filter(user=request.user).select_related('user','category').prefetch_related('likes','comments')
        return Response(ExpenseLogSerializer(qs, many=True, context={'request': request}).data)
    serializer = ExpenseLogCreateSerializer(data=request.data)
    if serializer.is_valid():
        log = serializer.save(user=request.user)
        return Response(ExpenseLogSerializer(log, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def log_detail(request, log_id):
    try: log = ExpenseLog.objects.select_related('user','category').get(id=log_id)
    except ExpenseLog.DoesNotExist: return Response({'detail':'소비 로그를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        if not can_view_log(request.user, log): return Response({'detail':'조회 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(ExpenseLogSerializer(log, context={'request': request}).data)
    if log.user_id != request.user.id: return Response({'detail':'작성자만 수정/삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        serializer = ExpenseLogCreateSerializer(log, data=request.data, partial=True)
        if serializer.is_valid():
            log = serializer.save(); return Response(ExpenseLogSerializer(log, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    log.delete(); return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_feed(request):
    rows = Friend.objects.filter(Q(user=request.user)|Q(friend=request.user), status=Friend.ACCEPTED)
    friend_ids = [row.friend_id if row.user_id == request.user.id else row.user_id for row in rows]
    qs = ExpenseLog.objects.filter(user_id__in=friend_ids, is_visible=True, expires_at__gt=timezone.now()).select_related('user','category').prefetch_related('likes','comments')
    return Response(ExpenseLogSerializer(qs, many=True, context={'request': request}).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, log_id):
    try: log = ExpenseLog.objects.get(id=log_id)
    except ExpenseLog.DoesNotExist: return Response({'detail':'소비 로그를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_view_log(request.user, log): return Response({'detail':'좋아요 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    like, created = Like.objects.get_or_create(user=request.user, log=log)
    if not created:
        like.delete(); return Response({'liked': False, 'like_count': log.likes.count()})
    return Response({'liked': True, 'like_count': log.likes.count()})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comments(request, log_id):
    try: log = ExpenseLog.objects.get(id=log_id)
    except ExpenseLog.DoesNotExist: return Response({'detail':'소비 로그를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_view_log(request.user, log): return Response({'detail':'댓글 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET': return Response(CommentSerializer(log.comments.select_related('user'), many=True).data)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(user=request.user, log=log)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
