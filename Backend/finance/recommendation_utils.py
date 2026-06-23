import json
import re

import requests
from django.conf import settings

from analysis.models import MonthlyAIAnalysis

from .finlife import to_int
from .models import FinancialProduct, FinancialProductRecommendation


DEFAULT_CAUTION = '본 추천은 참고용이며 실제 가입 전 금융회사 공식 정보와 약관을 반드시 확인해야 합니다.'


def option_rate(option):
    return option.intr_rate2 if option.intr_rate2 is not None else option.intr_rate or 0


def decimal_as_float(value):
    return float(value) if value is not None else None


def get_user_profile_data(user):
    try:
        profile = user.profile
    except Exception:
        return {}

    return {
        'nickname': profile.nickname,
        'bio': profile.bio,
    }


def matches_risk_term(risk_level, product_type, term):
    if term is None:
        return False
    if risk_level == 'high':
        return product_type == 'saving' and term <= 6
    if risk_level == 'low':
        return term >= 12
    return 6 <= term <= 12


def get_financial_product_candidates(user, analysis, limit=10):
    risk_level = getattr(analysis, 'risk_level', 'medium') or 'medium'
    products = FinancialProduct.objects.filter(is_active=True).prefetch_related('options')

    all_candidates = {}
    risk_candidates = {}
    for product in products:
        for option in product.options.all():
            term = to_int(option.save_trm)
            candidate = {
                'product_id': product.id,
                'option_id': option.id,
                'bank_name': product.kor_co_nm,
                'product_name': product.fin_prdt_nm,
                'product_type': product.product_type,
                'save_trm': option.save_trm,
                'interest_rate': decimal_as_float(option.intr_rate),
                'max_interest_rate': decimal_as_float(option.intr_rate2),
                'rate_for_sort': float(option_rate(option)),
                'join_way': product.join_way,
                'special_condition': product.spcl_cnd,
                'maturity_interest': product.mtrt_int,
                'join_member': product.join_member,
                'etc_note': product.etc_note,
                'rsrv_type_nm': option.rsrv_type_nm,
                'intr_rate_type_nm': option.intr_rate_type_nm,
            }
            current = all_candidates.get(product.id)
            if not current or candidate['rate_for_sort'] > current['rate_for_sort']:
                all_candidates[product.id] = candidate
            if matches_risk_term(risk_level, product.product_type, term):
                current = risk_candidates.get(product.id)
                if not current or candidate['rate_for_sort'] > current['rate_for_sort']:
                    risk_candidates[product.id] = candidate

    candidates = list((risk_candidates or all_candidates).values())
    candidates.sort(key=lambda item: item['rate_for_sort'], reverse=True)
    return candidates[:limit]


def strip_code_block(text):
    cleaned = (text or '').strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    start = cleaned.find('[')
    end = cleaned.rfind(']')
    if start != -1 and end != -1 and start < end:
        cleaned = cleaned[start:end + 1]
    return cleaned


def normalize_ai_recommendations(data):
    if not isinstance(data, list):
        return []

    recommendations = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            continue
        try:
            product_id = int(item.get('product_id'))
        except (TypeError, ValueError):
            continue

        recommendations.append(
            {
                'product_id': product_id,
                'title': str(item.get('title', '')).strip()[:100],
                'description': str(item.get('description', '')).strip(),
                'reason': str(item.get('reason', '')).strip(),
                'action_text': str(item.get('action_text', '')).strip()[:100],
                'ai_comment': str(item.get('ai_comment', '')).strip(),
                'caution': str(item.get('caution', '')).strip() or DEFAULT_CAUTION,
                'priority': int(item.get('priority') or index),
            }
        )
    return recommendations


def parse_ai_recommendations(text):
    data = json.loads(strip_code_block(text))
    return normalize_ai_recommendations(data)


def build_recommendation_prompt(user, analysis, candidates):
    analysis_data = None
    if analysis:
        analysis_data = {
            'year': analysis.year,
            'month': analysis.month,
            'total_amount': analysis.total_amount,
            'log_count': analysis.log_count,
            'average_amount': analysis.average_amount,
            'category_summary': analysis.category_summary,
            'summary': analysis.summary,
            'problem': analysis.problem,
            'feedback': analysis.feedback,
            'saving_tip': analysis.saving_tip,
            'risk_level': analysis.risk_level,
        }

    payload = {
        'user': {
            'username': user.username,
            'name': user.name,
            'profile': get_user_profile_data(user),
        },
        'latest_monthly_ai_analysis': analysis_data,
        'financial_product_candidates': candidates,
    }

    return (
        '사용자의 소비 분석, 프로필, 금융상품 후보를 바탕으로 참고용 금융상품 추천을 작성하세요.\n'
        '예금/적금 상품만 추천하고 주식 매수/매도 권유는 하지 마세요.\n'
        '상품 가입을 강하게 권유하지 말고, 금리 조건과 중도해지 조건 확인을 안내하세요.\n'
        '반드시 JSON 배열만 응답하세요. 마크다운 코드블록과 설명 문장은 포함하지 마세요.\n\n'
        '응답 형식:\n'
        '[{"product_id":1,"title":"추천 제목","description":"설명","reason":"추천 이유",'
        '"action_text":"상품 조건 확인하기","ai_comment":"AI 코멘트",'
        '"caution":"참고용 추천이며 가입 전 공식 정보를 확인하세요.","priority":1}]\n\n'
        f'입력 데이터:\n{json.dumps(payload, ensure_ascii=False)}'
    )


def request_gms_financial_recommendations(user, analysis, candidates):
    if not settings.GMS_KEY or not candidates:
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
                    '당신은 소비 분석 기반 금융상품 추천 보조자입니다. '
                    '추천은 참고용으로만 표현하고, 주식 매수/매도 추천은 금지합니다. '
                    '반드시 유효한 JSON 배열만 응답합니다.'
                ),
            },
            {
                'role': 'user',
                'content': build_recommendation_prompt(user, analysis, candidates),
            },
        ],
        'temperature': 0.2,
    }

    try:
        response = requests.post(
            settings.GMS_API_URL,
            headers=headers,
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return parse_ai_recommendations(content)
    except (
        requests.RequestException,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None


def fallback_recommendations(analysis, candidates, limit=3):
    risk_level = getattr(analysis, 'risk_level', 'medium') or 'medium'
    if not candidates:
        return [
            {
                'product_id': None,
                'title': '추천 가능한 금융상품 데이터가 없습니다',
                'description': '먼저 금융상품 fixture를 DB에 로드한 뒤 추천을 다시 요청해 주세요.',
                'reason': 'DB에 정기예금/정기적금 상품 정보가 없어 상품 기반 추천을 만들 수 없습니다.',
                'action_text': '상품 데이터 로드하기',
                'ai_comment': '',
                'caution': DEFAULT_CAUTION,
                'priority': 1,
            }
        ]

    if risk_level == 'high':
        base_title = '소비 개선을 우선하면서 작게 시작할 수 있는 상품입니다'
        base_reason = (
            '최근 소비 위험도가 높으므로 큰 금액을 장기간 묶기보다 '
            '6개월 이하 단기 적금이나 부담이 낮은 저축 습관을 먼저 검토하는 편이 좋습니다.'
        )
    elif risk_level == 'low':
        base_title = '안정적으로 목돈을 묶어둘 수 있는 상품입니다'
        base_reason = '최근 소비 위험도가 낮아 12개월 이상 예금/적금 후보를 우선 검토할 수 있습니다.'
    else:
        base_title = '6~12개월 동안 무리 없이 검토할 수 있는 상품입니다'
        base_reason = '최근 소비 위험도가 보통이므로 중기 예금/적금 후보를 우선 추천합니다.'

    results = []
    for index, candidate in enumerate(candidates[:limit], start=1):
        results.append(
            {
                'product_id': candidate['product_id'],
                'title': base_title,
                'description': (
                    f"{candidate['bank_name']}의 {candidate['product_name']}은 "
                    f"{candidate['save_trm']}개월 기준 최고금리 후보입니다."
                ),
                'reason': base_reason,
                'action_text': '상품 조건 확인하기',
                'ai_comment': '가입 조건, 우대 조건, 중도해지 이율을 확인하세요.',
                'caution': DEFAULT_CAUTION,
                'priority': index,
            }
        )
    return results


def get_best_option(product):
    options = list(product.options.all())
    if not options:
        return None
    return max(options, key=option_rate)


def save_recommendations(user, analysis, payloads, candidates):
    candidate_by_product_id = {}
    for candidate in candidates:
        candidate_by_product_id.setdefault(candidate['product_id'], candidate)

    saved = []
    seen_product_ids = set()
    for index, payload in enumerate(payloads, start=1):
        product = None
        candidate = None
        product_id = payload.get('product_id')
        if product_id:
            if product_id in seen_product_ids:
                continue
            try:
                product = FinancialProduct.objects.prefetch_related('options').get(
                    id=product_id,
                    is_active=True,
                )
            except FinancialProduct.DoesNotExist:
                continue
            candidate = candidate_by_product_id.get(product.id)
            seen_product_ids.add(product.id)

        option = None
        if product and not candidate:
            option = get_best_option(product)
        if product and candidate:
            option = product.options.filter(id=candidate['option_id']).first()
            bank_name = candidate['bank_name']
            product_name = candidate['product_name']
            product_type = candidate['product_type']
            save_trm = candidate['save_trm']
            interest_rate = candidate['interest_rate']
            max_interest_rate = candidate['max_interest_rate']
        elif product:
            bank_name = product.kor_co_nm
            product_name = product.fin_prdt_nm
            product_type = product.product_type
            save_trm = option.save_trm if option else ''
            interest_rate = option.intr_rate if option else None
            max_interest_rate = option.intr_rate2 if option else None
        else:
            bank_name = ''
            product_name = ''
            product_type = ''
            save_trm = ''
            interest_rate = None
            max_interest_rate = None

        recommendation = FinancialProductRecommendation.objects.create(
            user=user,
            analysis=analysis,
            product=product,
            option=option,
            title=payload.get('title') or '금융상품 추천',
            description=payload.get('description') or '',
            reason=payload.get('reason') or '',
            action_text=payload.get('action_text') or '상품 조건 확인하기',
            bank_name=bank_name,
            product_name=product_name,
            product_type=product_type,
            save_trm=save_trm,
            interest_rate=interest_rate,
            max_interest_rate=max_interest_rate,
            ai_comment=payload.get('ai_comment') or '',
            caution=payload.get('caution') or DEFAULT_CAUTION,
            priority=payload.get('priority') or index,
        )
        saved.append(recommendation)
    return saved


def create_financial_product_recommendations(user):
    analysis = MonthlyAIAnalysis.objects.filter(user=user).first()
    candidates = get_financial_product_candidates(user, analysis, limit=10)
    ai_payloads = request_gms_financial_recommendations(user, analysis, candidates)
    payloads = ai_payloads or fallback_recommendations(analysis, candidates)
    recommendations = save_recommendations(user, analysis, payloads, candidates)

    if not recommendations and ai_payloads:
        payloads = fallback_recommendations(analysis, candidates)
        recommendations = save_recommendations(user, analysis, payloads, candidates)

    return recommendations
