from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from expenses.models import ExpenseLog
from .models import AIAnalysis, MonthlyAnalysis
from .serializers import AIAnalysisSerializer, MonthlyAnalysisSerializer
from .services import build_rule_feedback, call_ai_api

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_list(request):
    return Response(MonthlyAnalysisSerializer(MonthlyAnalysis.objects.filter(user=request.user), many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_monthly_analysis(request):
    year = int(request.data.get('year'))
    month = int(request.data.get('month'))
    logs = ExpenseLog.objects.filter(user=request.user, created_at__year=year, created_at__month=month)
    total = logs.aggregate(total=Sum('amount'))['total'] or 0
    summary = {r['category__name']: r['total'] for r in logs.values('category__name').annotate(total=Sum('amount'))}
    obj, _ = MonthlyAnalysis.objects.update_or_create(user=request.user, year=year, month=month, defaults={'total_amount': total, 'category_summary': summary})
    return Response(MonthlyAnalysisSerializer(obj).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_list(request):
    return Response(AIAnalysisSerializer(AIAnalysis.objects.filter(user=request.user), many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ai_analysis(request):
    try:
        monthly = MonthlyAnalysis.objects.get(id=request.data.get('analysis_id'), user=request.user)
    except MonthlyAnalysis.DoesNotExist:
        return Response({'detail':'월별 분석 데이터를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    input_summary = (
        f'분석 월: {monthly.year}-{monthly.month}\n'
        f'총 소비: {monthly.total_amount}\n'
        f'카테고리별: {monthly.category_summary}'
    )
    ai_result = call_ai_api(input_summary)
    if ai_result:
        result = feedback = ai_result; ai_status = AIAnalysis.SUCCESS
    else:
        feedback = build_rule_feedback(monthly.total_amount, monthly.category_summary)
        result = 'AI API 키가 없거나 호출에 실패하여 규칙 기반 피드백을 제공했습니다.'
        ai_status = AIAnalysis.FALLBACK
    obj = AIAnalysis.objects.create(user=request.user, analysis=monthly, input_summary=input_summary, result=result, feedback=feedback, status=ai_status)
    return Response(AIAnalysisSerializer(obj).data, status=status.HTTP_201_CREATED)
