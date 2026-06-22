import requests
from django.conf import settings


class KakaoLocalAPIError(Exception):
    pass


def _request(path, params):
    if not settings.KAKAO_REST_API_KEY:
        raise KakaoLocalAPIError('KAKAO_REST_API_KEY가 설정되지 않았습니다.')
    try:
        response = requests.get(
            f'{settings.KAKAO_LOCAL_API_BASE_URL.rstrip("/")}/{path}',
            params=params,
            headers={'Authorization': f'KakaoAK {settings.KAKAO_REST_API_KEY}'},
            timeout=settings.EXTERNAL_API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise KakaoLocalAPIError('Kakao Local API 요청에 실패했습니다.') from None


def resolve_location(query):
    address_payload = _request('search/address.json', {'query': query, 'size': 1})
    documents = address_payload.get('documents', [])
    if not documents:
        keyword_payload = _request('search/keyword.json', {'query': query, 'size': 1})
        documents = keyword_payload.get('documents', [])
    if not documents:
        raise KakaoLocalAPIError('입력한 위치를 찾을 수 없습니다.')
    item = documents[0]
    return {
        'name': item.get('place_name') or item.get('address_name') or query,
        'address': item.get('road_address_name') or item.get('address_name') or '',
        'x': float(item['x']),
        'y': float(item['y']),
    }


def search_nearby_banks(query, radius=2000):
    center = resolve_location(query)
    payload = _request(
        'search/category.json',
        {
            'category_group_code': 'BK9',
            'x': center['x'],
            'y': center['y'],
            'radius': radius,
            'sort': 'distance',
            'size': 15,
        },
    )
    banks = []
    for item in payload.get('documents', []):
        banks.append(
            {
                'id': item.get('id'),
                'name': item.get('place_name', ''),
                'address': item.get('address_name', ''),
                'road_address': item.get('road_address_name', ''),
                'phone': item.get('phone', ''),
                'distance': int(item.get('distance') or 0),
                'place_url': item.get('place_url', ''),
                'x': float(item['x']),
                'y': float(item['y']),
            }
        )
    return {'center': center, 'banks': banks}
