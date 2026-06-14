from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from analysis.models import AIAnalysis
from .models import FinancialProduct, ProductRecommendation
from .serializers import FinancialProductSerializer, ProductRecommendationSerializer
from .services import choose_products, seed_sample_products

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products(request):
    return Response(FinancialProductSerializer(FinancialProduct.objects.all(), many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seed_products(request):
    seed_sample_products(); return Response({'message':'샘플 금융상품이 저장되었습니다.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    qs = ProductRecommendation.objects.filter(user=request.user).select_related('product','ai_analysis')
    return Response(ProductRecommendationSerializer(qs, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_recommendations(request):
    try:
        ai = AIAnalysis.objects.select_related('analysis').get(id=request.data.get('ai_analysis_id'), user=request.user)
    except AIAnalysis.DoesNotExist:
        return Response({'detail':'AI 분석 결과를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    ProductRecommendation.objects.filter(user=request.user, ai_analysis=ai).delete()
    created=[]
    for idx, product in enumerate(choose_products(ai.analysis), start=1):
        reason = '소비 습관 개선을 위해 매월 일정 금액을 저축하는 데 적합한 상품입니다.' if product.product_type == FinancialProduct.SAVING else '여유 자금을 안정적으로 관리하는 데 적합한 상품입니다.'
        created.append(ProductRecommendation.objects.create(user=request.user, ai_analysis=ai, product=product, reason=reason, priority=idx))
    return Response(ProductRecommendationSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
