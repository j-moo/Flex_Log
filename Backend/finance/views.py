from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FinancialProduct, FinancialProductRecommendation, StockHolding
from .recommendation_utils import create_financial_product_recommendations
from .serializers import (
    FinancialProductRecommendationSerializer,
    FinancialProductSerializer,
    StockHoldingSerializer,
)


def apply_product_filters(request, product_type=None):
    query_type = product_type or request.query_params.get('type')
    queryset = FinancialProduct.objects.filter(is_active=True).prefetch_related('options')

    if query_type:
        if query_type not in {'deposit', 'saving'}:
            return None, Response(
                {'detail': 'type은 deposit 또는 saving만 사용할 수 있습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.filter(product_type=query_type)

    bank = request.query_params.get('bank')
    if bank:
        queryset = queryset.filter(kor_co_nm__icontains=bank.strip())

    term = request.query_params.get('term')
    if term:
        queryset = queryset.filter(options__save_trm=str(term).strip())

    min_rate = request.query_params.get('min_rate')
    if min_rate:
        try:
            min_rate_value = float(min_rate)
        except (TypeError, ValueError):
            return None, Response(
                {'detail': 'min_rate는 숫자여야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.filter(
            Q(options__intr_rate__gte=min_rate_value)
            | Q(options__intr_rate2__gte=min_rate_value)
        )

    return queryset.distinct(), None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    queryset, error_response = apply_product_filters(request)
    if error_response:
        return error_response
    return Response(FinancialProductSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deposit_product_list(request):
    queryset, error_response = apply_product_filters(request, 'deposit')
    if error_response:
        return error_response
    return Response(FinancialProductSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saving_product_list(request):
    queryset, error_response = apply_product_filters(request, 'saving')
    if error_response:
        return error_response
    return Response(FinancialProductSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    try:
        product = FinancialProduct.objects.prefetch_related('options').get(
            id=product_id,
            is_active=True,
        )
    except FinancialProduct.DoesNotExist:
        return Response(
            {'detail': '금융상품을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(FinancialProductSerializer(product).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_products(request):
    recommendations = create_financial_product_recommendations(request.user)
    return Response(
        FinancialProductRecommendationSerializer(recommendations, many=True).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_recommendations(request):
    recommendations = FinancialProductRecommendation.objects.filter(
        user=request.user,
    ).order_by('-created_at', 'priority')[:5]
    return Response(
        FinancialProductRecommendationSerializer(recommendations, many=True).data
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendation_history(request):
    recommendations = FinancialProductRecommendation.objects.filter(
        user=request.user,
    ).order_by('-created_at', 'priority')
    return Response(
        FinancialProductRecommendationSerializer(recommendations, many=True).data
    )


class StockHoldingListCreateView(generics.ListCreateAPIView):
    serializer_class = StockHoldingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return StockHolding.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StockHoldingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StockHoldingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return StockHolding.objects.filter(user=self.request.user)
