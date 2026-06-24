from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related('actor', 'actor__profile')
            .order_by('-created_at')[:80]
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    notification = generics.get_object_or_404(
        Notification.objects.filter(user=request.user),
        pk=pk,
    )
    notification.mark_read()
    return Response(NotificationSerializer(notification).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    now = timezone.now()
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=now,
    )
    return Response(status=status.HTTP_204_NO_CONTENT)
