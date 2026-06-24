import json
import re
from datetime import datetime

import requests
from django.conf import settings
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from expenses.models import ExpenseLog
from notifications.helpers import create_notification
from notifications.models import Notification

from .models import MonthlyAIAnalysis, MonthlyAnalysis
from .serializers import (
    MonthlyAIAnalysisRequestSerializer,
    MonthlyAIAnalysisSerializer,
    MonthlyAnalysisSerializer,
)


def month_range(year, month):
    start = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end = timezone.make_aware(datetime(year, month + 1, 1))
    return start, end


def aggregate_monthly_expenses(user, year, month):
    start, end = month_range(year, month)
    logs = ExpenseLog.objects.filter(user=user, created_at__gte=start, created_at__lt=end)
    category_rows = logs.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id'),
    )

    category_summary = {}
    for row in category_rows:
        name = row['category__name'] or '기타'
        category_summary[name] = {
            'total': int(row['total'] or 0),
            'count': int(row['count'] or 0),
        }

    total_amount = sum(item['total'] for item in category_summary.values())
    log_count = logs.count()
    average_amount = total_amount // log_count if log_count else 0

    return {
        'year': year,
        'month': month,
        'total_amount': total_amount,
        'log_count': log_count,
        'average_amount': average_amount,
        'category_summary': category_summary,
    }


def save_basic_monthly_analysis(user, data):
    simple_summary = {
        name: values['total']
        for name, values in data['category_summary'].items()
    }
    analysis, _ = MonthlyAnalysis.objects.update_or_create(
        user=user,
        year=data['year'],
        month=data['month'],
        defaults={
            'total_amount': data['total_amount'],
            'category_summary': simple_summary,
        },
    )
    return analysis


def strip_code_block(text):
    cleaned = (text or '').strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and start < end:
        cleaned = cleaned[start:end + 1]
    return cleaned


def parse_ai_json(text):
    data = json.loads(strip_code_block(text))
    return normalize_ai_result(data)


def normalize_ai_result(data):
    risk_level = str(data.get('risk_level', 'medium')).strip().lower()
    if risk_level not in {'low', 'medium', 'high'}:
        risk_level = 'medium'

    return {
        'summary': str(data.get('summary', '')).strip(),
        'problem': str(data.get('problem', '')).strip(),
        'feedback': str(data.get('feedback', '')).strip(),
        'saving_tip': str(data.get('saving_tip', '')).strip(),
        'risk_level': risk_level,
    }


def build_ai_prompt(data):
    return (
        '다음 월별 소비 집계 데이터를 바탕으로 소비 패턴을 분석해 주세요.\n'
        'monthly_income 값이 0보다 크면 월 수입 대비 소비 비율을 위험도 판단의 핵심 기준으로 사용하세요.\n'
        '반드시 아래 키만 가진 한국어 JSON 객체로만 답하세요.\n'
        '마크다운 코드블록, 설명 문장, 추가 텍스트는 포함하지 마세요.\n\n'
        '필수 형식:\n'
        '{'
        '"summary":"이번 달 소비 패턴 요약",'
        '"problem":"가장 중요한 소비 문제점",'
        '"feedback":"소비 습관 개선 피드백",'
        '"saving_tip":"실천 가능한 절약 팁",'
        '"risk_level":"low 또는 medium 또는 high"'
        '}\n\n'
        f'소비 집계 데이터:\n{json.dumps(data, ensure_ascii=False)}'
    )


def request_gms_analysis(data):
    if not settings.GMS_KEY:
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.GMS_KEY}',
    }
    payload = {
        'model': settings.GMS_MODEL,
        'messages': [
            {
                'role': 'developer',
                'content': (
                    '당신은 사용자의 월별 소비 기록을 분석하는 금융 소비 습관 코치입니다. '
                    '투자 권유가 아니라 소비 습관 개선 조언만 제공합니다. '
                    '반드시 유효한 한국어 JSON으로만 답합니다.'
                ),
            },
            {
                'role': 'user',
                'content': build_ai_prompt(data),
            },
        ],
        'temperature': 0.3,
    }

    try:
        response = requests.post(
            settings.GMS_API_URL,
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return parse_ai_json(content)
    except (
        requests.RequestException,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None


def calculate_risk_level(data):
    total_amount = data['total_amount']
    monthly_income = int(data.get('monthly_income') or 0)
    if monthly_income > 0:
        income_ratio = total_amount / monthly_income
        if income_ratio >= 0.9:
            return 'high'
        if income_ratio >= 0.6:
            return 'medium'
        return 'low'

    if total_amount >= 1_000_000:
        return 'high'
    if total_amount >= 500_000:
        return 'medium'
    return 'low'


def fallback_analysis(data):
    if data['log_count'] == 0:
        return {
            'summary': '아직 분석할 소비 기록이 부족합니다.',
            'problem': '이번 달에 저장된 소비 로그가 없습니다.',
            'feedback': '소비 직후 금액, 카테고리, 장소를 간단히 기록하는 습관부터 만들어보세요.',
            'saving_tip': '오늘 소비 1건만 먼저 기록하고 월말에 패턴을 확인해 보세요.',
            'risk_level': 'low',
        }

    total_amount = data['total_amount']
    monthly_income = int(data.get('monthly_income') or 0)
    risk_level = calculate_risk_level(data)
    income_ratio = round((total_amount / monthly_income) * 100, 1) if monthly_income else None

    top_name, top_data = max(
        data['category_summary'].items(),
        key=lambda item: item[1]['total'],
    )
    top_total = top_data['total']
    top_count = top_data['count']

    return {
        'summary': (
            f"{data['year']}년 {data['month']}월에는 총 {total_amount:,}원을 "
            f"{data['log_count']}건에 사용했고, 평균 소비 금액은 {data['average_amount']:,}원입니다."
            + (
                f" 월 수입 {monthly_income:,}원 대비 {income_ratio}%를 사용했습니다."
                if monthly_income
                else ''
            )
        ),
        'problem': f'{top_name} 지출이 {top_total:,}원, {top_count}건으로 가장 큽니다.',
        'feedback': f'{top_name} 소비를 먼저 점검하면 전체 지출을 줄이는 효과가 큽니다.',
        'saving_tip': f'다음 주에는 {top_name} 카테고리에 주간 한도를 정하고 기록해 보세요.',
        'risk_level': risk_level,
    }


def create_monthly_ai_analysis(user, data, ai_result):
    return MonthlyAIAnalysis.objects.create(
        user=user,
        year=data['year'],
        month=data['month'],
        total_amount=data['total_amount'],
        log_count=data['log_count'],
        average_amount=data['average_amount'],
        category_summary=data['category_summary'],
        summary=ai_result['summary'],
        problem=ai_result['problem'],
        feedback=ai_result['feedback'],
        saving_tip=ai_result['saving_tip'],
        risk_level=ai_result['risk_level'],
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def monthly_analysis(request):
    if request.method == 'GET':
        today = timezone.localdate()
        serializer = MonthlyAIAnalysisRequestSerializer(
            data={
                'year': request.query_params.get('year', today.year),
                'month': request.query_params.get('month', today.month),
            },
        )
        serializer.is_valid(raise_exception=True)
        year = serializer.validated_data['year']
        month = serializer.validated_data['month']
        data = aggregate_monthly_expenses(request.user, year, month)
        basic_analysis = save_basic_monthly_analysis(request.user, data)
        response_data = MonthlyAnalysisSerializer(basic_analysis).data
        response_data['log_count'] = data['log_count']
        response_data['average_amount'] = data['average_amount']
        return Response(response_data)

    serializer = MonthlyAIAnalysisRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    year = serializer.validated_data['year']
    month = serializer.validated_data['month']
    data = aggregate_monthly_expenses(request.user, year, month)
    data['monthly_income'] = serializer.validated_data.get('monthly_income', 0)
    save_basic_monthly_analysis(request.user, data)

    ai_result = request_gms_analysis(data) or fallback_analysis(data)
    if data['monthly_income'] > 0:
        ai_result['risk_level'] = calculate_risk_level(data)
    analysis = create_monthly_ai_analysis(request.user, data, ai_result)
    create_notification(
        user=request.user,
        notification_type=Notification.Type.AI_ANALYSIS,
        title='AI 분석 완료',
        message=f'{year}년 {month}월 소비 AI 분석 결과가 준비되었습니다.',
        target_route='analysis',
        dedupe_key=f'ai-analysis:{analysis.id}',
    )

    return Response(
        MonthlyAIAnalysisSerializer(analysis).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_monthly_analysis(request):
    analysis = MonthlyAIAnalysis.objects.filter(user=request.user).first()
    if not analysis:
        return Response(
            {'detail': '아직 생성된 AI 분석 결과가 없습니다.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(MonthlyAIAnalysisSerializer(analysis).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_analysis_history(request):
    analyses = MonthlyAIAnalysis.objects.filter(user=request.user)
    return Response(MonthlyAIAnalysisSerializer(analyses, many=True).data)
