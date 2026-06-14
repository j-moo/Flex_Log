import os
import requests


def build_rule_feedback(total_amount, category_summary):
    if total_amount == 0:
        return '아직 소비 기록이 충분하지 않습니다. 소비 로그를 먼저 작성해보세요.'

    top_category, top_amount = max(category_summary.items(), key=lambda x: x[1]) if category_summary else ('기타', 0)
    ratio = round(top_amount / total_amount * 100, 1) if total_amount else 0

    messages = [
        f'이번 달 총 소비금액은 {total_amount:,}원입니다.',
        f'가장 큰 소비 카테고리는 {top_category}이며 전체의 {ratio}%입니다.',
    ]

    if ratio >= 40:
        messages.append(f'{top_category} 비중이 높습니다. 다음 달 예산 상한을 정해보세요.')
    else:
        messages.append('소비가 한 카테고리에 과도하게 집중되지는 않았습니다.')

    if category_summary.get('카페', 0) >= 80000:
        messages.append('카페 소비가 높은 편입니다. 주간 카페 예산을 정해보세요.')

    return '\n'.join(messages)


def call_ai_api(input_summary):
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    if not api_key:
        return None

    prompt = '다음 소비 데이터를 한국어로 요약하고 개선방안과 추천 금융상품 유형을 제안해줘.\n' + input_summary

    try:
        res = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.4,
            },
            timeout=20,
        )
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except Exception:
        return None
