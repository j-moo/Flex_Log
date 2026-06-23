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


def _mobility_request(path, params):
    api_key = getattr(settings, 'KAKAO_MOBILITY_API_KEY', None) or settings.KAKAO_REST_API_KEY
    if not api_key:
        raise KakaoLocalAPIError('KAKAO_MOBILITY_API_KEY 또는 KAKAO_REST_API_KEY가 설정되지 않았습니다.')
    try:
        response = requests.get(
            f'{settings.KAKAO_MOBILITY_API_BASE_URL.rstrip("/")}/{path}',
            params=params,
            headers={
                'Authorization': f'KakaoAK {api_key}',
                'Content-Type': 'application/json',
            },
            timeout=settings.EXTERNAL_API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise KakaoLocalAPIError('Kakao Mobility API 요청에 실패했습니다.') from None


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


def search_driving_route(destination_x, destination_y, destination_name=''):
    origin_x = getattr(settings, 'KAKAO_ROUTE_ORIGIN_X', 127.039585)
    origin_y = getattr(settings, 'KAKAO_ROUTE_ORIGIN_Y', 37.5012743)
    origin_name = getattr(settings, 'KAKAO_ROUTE_ORIGIN_NAME', '멀티캠퍼스 역삼')

    destination = f'{destination_x},{destination_y}'
    if destination_name:
        destination = f'{destination},name={destination_name}'

    payload = _mobility_request(
        'v1/directions',
        {
            'origin': f'{origin_x},{origin_y},name={origin_name}',
            'destination': destination,
            'priority': 'RECOMMEND',
            'car_fuel': 'GASOLINE',
            'car_hipass': 'false',
            'alternatives': 'false',
            'road_details': 'false',
            'summary': 'false',
        },
    )
    routes = payload.get('routes') or []
    if not routes:
        raise KakaoLocalAPIError('이동 경로를 찾을 수 없습니다.')

    route = routes[0]
    if route.get('result_code', 0) != 0:
        raise KakaoLocalAPIError(route.get('result_msg') or '이동 경로를 찾을 수 없습니다.')

    path = []
    for section in route.get('sections') or []:
        for road in section.get('roads') or []:
            vertexes = road.get('vertexes') or []
            for index in range(0, len(vertexes) - 1, 2):
                path.append({'x': float(vertexes[index]), 'y': float(vertexes[index + 1])})

    if not path:
        raise KakaoLocalAPIError('지도에 표시할 경로 좌표가 없습니다.')

    summary = route.get('summary') or {}
    return {
        'origin': {'name': origin_name, 'x': float(origin_x), 'y': float(origin_y)},
        'destination': {
            'name': destination_name,
            'x': float(destination_x),
            'y': float(destination_y),
        },
        'summary': {
            'distance': int(summary.get('distance') or 0),
            'duration': int(summary.get('duration') or 0),
            'fare': summary.get('fare') or {},
        },
        'path': path,
    }
