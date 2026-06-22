from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Commodity,
    CommodityPrice,
    FinancialProduct,
    FinancialProductRecommendation,
    StockHolding,
    UserFinancialProduct,
)
from .recommendation_utils import create_financial_product_recommendations
from .serializers import (
    CommodityPriceImportSerializer,
    CommodityPriceSerializer,
    CommoditySerializer,
    FinancialProductRecommendationSerializer,
    FinancialProductSerializer,
    StockHoldingSerializer,
    UserFinancialProductSerializer,
)
from .services.kiwoom_api import get_chart, get_quote
from .services.kiwoom_auth import KiwoomAPIError
from .services.kakao_local import KakaoLocalAPIError, search_nearby_banks
from .services.youtube_api import YouTubeAPIError, get_video_detail, search_videos


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


class UserFinancialProductListCreateView(generics.ListCreateAPIView):
    serializer_class = UserFinancialProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserFinancialProduct.objects.filter(user=self.request.user).select_related(
            'option',
            'option__product',
        ).prefetch_related('option__product__options')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        option = input_serializer.validated_data['option']
        subscription = UserFinancialProduct.objects.select_for_update().filter(
            user=request.user,
            option=option,
        ).first()

        if subscription and subscription.status == UserFinancialProduct.Status.ACTIVE:
            return Response(
                {'detail': '이미 가입 중인 금융상품 옵션입니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if subscription:
            subscription.status = UserFinancialProduct.Status.ACTIVE
            subscription.joined_at = timezone.now()
            subscription.cancelled_at = None
            subscription.save(
                update_fields=('status', 'joined_at', 'cancelled_at', 'updated_at'),
            )
        else:
            subscription = UserFinancialProduct.objects.create(
                user=request.user,
                option=option,
            )

        output_serializer = self.get_serializer(subscription)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cancel_financial_product(request, subscription_id):
    subscription = get_object_or_404(
        UserFinancialProduct.objects.select_for_update().select_related(
            'option',
            'option__product',
        ).prefetch_related('option__product__options'),
        id=subscription_id,
        user=request.user,
    )
    if subscription.status == UserFinancialProduct.Status.CANCELLED:
        return Response(
            {'detail': '이미 해지된 금융상품입니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    subscription.status = UserFinancialProduct.Status.CANCELLED
    subscription.cancelled_at = timezone.now()
    subscription.save(update_fields=('status', 'cancelled_at', 'updated_at'))
    return Response(UserFinancialProductSerializer(subscription).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commodity_list(request):
    commodities = Commodity.objects.all()
    return Response(CommoditySerializer(commodities, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commodity_price_list(request, code):
    commodity = get_object_or_404(Commodity, code=code.upper())
    prices = commodity.prices.all()

    start = request.query_params.get('start')
    end = request.query_params.get('end')
    start_date = parse_date(start) if start else None
    end_date = parse_date(end) if end else None
    if start and start_date is None:
        return Response(
            {'detail': 'start는 YYYY-MM-DD 형식이어야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if end and end_date is None:
        return Response(
            {'detail': 'end는 YYYY-MM-DD 형식이어야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if start_date and end_date and start_date > end_date:
        return Response(
            {'detail': 'start는 end보다 늦을 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if start_date:
        prices = prices.filter(price_date__gte=start_date)
    if end_date:
        prices = prices.filter(price_date__lte=end_date)

    return Response(
        {
            'commodity': CommoditySerializer(commodity).data,
            'prices': CommodityPriceSerializer(prices, many=True).data,
        },
    )


@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def import_commodity_prices(request):
    serializer = CommodityPriceImportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    code = data['code']
    default_names = {'GOLD': '금', 'SILVER': '은'}
    commodity, _ = Commodity.objects.update_or_create(
        code=code,
        defaults={
            'name': data.get('name', default_names[code]),
            'unit': data['unit'],
            'currency': data['currency'],
        },
    )

    created_count = 0
    updated_count = 0
    default_source = data['source']
    for item in data['prices']:
        price_data = dict(item)
        price_date = price_data.pop('price_date')
        if not price_data.get('source'):
            price_data['source'] = default_source
        _, created = CommodityPrice.objects.update_or_create(
            commodity=commodity,
            price_date=price_date,
            defaults=price_data,
        )
        created_count += int(created)
        updated_count += int(not created)

    return Response(
        {
            'commodity': CommoditySerializer(commodity).data,
            'created': created_count,
            'updated': updated_count,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def youtube_video_search(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response(
            {'detail': 'q 검색어가 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        max_results = int(request.query_params.get('max_results', 12))
    except (TypeError, ValueError):
        return Response(
            {'detail': 'max_results는 숫자여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    max_results = min(max(max_results, 1), 25)
    try:
        videos = search_videos(query, max_results)
    except YouTubeAPIError as exc:
        return Response(
            {'detail': str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response({'query': query, 'videos': videos})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def youtube_video_detail(request, video_id):
    try:
        video = get_video_detail(video_id)
    except YouTubeAPIError as exc:
        return Response(
            {'detail': str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(video)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_bank_search(request):
    query = request.query_params.get('query', '').strip()
    if not query:
        return Response(
            {'detail': 'query 위치가 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        radius = int(request.query_params.get('radius', 2000))
    except (TypeError, ValueError):
        return Response(
            {'detail': 'radius는 숫자여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not 100 <= radius <= 20000:
        return Response(
            {'detail': 'radius는 100~20000m 범위여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        return Response(search_nearby_banks(query, radius))
    except KakaoLocalAPIError as exc:
        return Response(
            {'detail': str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_quote(request):
    symbol = request.query_params.get('symbol')
    if not symbol:
        return Response(
            {'detail': 'symbol query parameter is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        return Response(get_quote(symbol))
    except KiwoomAPIError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_chart(request):
    symbol = request.query_params.get('symbol')
    period = request.query_params.get('period', '1m')
    if not symbol:
        return Response(
            {'detail': 'symbol query parameter is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        return Response(get_chart(symbol, period))
    except KiwoomAPIError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


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
