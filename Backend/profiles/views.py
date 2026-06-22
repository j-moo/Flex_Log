from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from finance.models import UserFinancialProduct

from .models import Profile
from .serializers import ProfileSerializer


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={'nickname': self.request.user.username},
        )
        return Profile.objects.select_related('user').prefetch_related(
            Prefetch(
                'user__joined_financial_products',
                queryset=UserFinancialProduct.objects.filter(
                    status=UserFinancialProduct.Status.ACTIVE,
                ).select_related('option', 'option__product').prefetch_related(
                    'option__product__options',
                ),
                to_attr='active_joined_products',
            ),
        ).get(pk=profile.pk)


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        return Profile.objects.select_related('user').prefetch_related(
            Prefetch(
                'user__joined_financial_products',
                queryset=UserFinancialProduct.objects.filter(
                    status=UserFinancialProduct.Status.ACTIVE,
                ).select_related('option', 'option__product').prefetch_related(
                    'option__product__options',
                ),
                to_attr='active_joined_products',
            ),
        )
