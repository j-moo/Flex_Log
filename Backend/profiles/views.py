from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'nickname': request.user.username})
    if request.method == 'GET':
        return Response(ProfileSerializer(profile).data)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_detail(request, user_id):
    try:
        profile = Profile.objects.select_related('user').get(user_id=user_id)
    except Profile.DoesNotExist:
        return Response({'detail': '프로필을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ProfileSerializer(profile).data)
