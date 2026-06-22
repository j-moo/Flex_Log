import requests
from django.conf import settings


class YouTubeAPIError(Exception):
    pass


def _request(path, params):
    if not settings.YOUTUBE_API_KEY:
        raise YouTubeAPIError('YOUTUBE_API_KEY가 설정되지 않았습니다.')
    try:
        response = requests.get(
            f'{settings.YOUTUBE_API_BASE_URL.rstrip("/")}/{path}',
            params={**params, 'key': settings.YOUTUBE_API_KEY},
            timeout=settings.EXTERNAL_API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        message = 'YouTube API 요청에 실패했습니다.'
        if exc.response is not None:
            try:
                message = exc.response.json()['error']['message']
            except (ValueError, KeyError, TypeError):
                pass
        raise YouTubeAPIError(message) from None


def _video_from_item(item):
    snippet = item.get('snippet') or {}
    video_id = item.get('id')
    if isinstance(video_id, dict):
        video_id = video_id.get('videoId')
    thumbnails = snippet.get('thumbnails') or {}
    thumbnail = thumbnails.get('high') or thumbnails.get('medium') or thumbnails.get('default') or {}
    return {
        'video_id': video_id,
        'title': snippet.get('title', ''),
        'description': snippet.get('description', ''),
        'channel_title': snippet.get('channelTitle', ''),
        'published_at': snippet.get('publishedAt'),
        'thumbnail_url': thumbnail.get('url', ''),
    }


def search_videos(query, max_results=12):
    payload = _request(
        'search',
        {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'safeSearch': 'moderate',
            'relevanceLanguage': 'ko',
        },
    )
    return [_video_from_item(item) for item in payload.get('items', [])]


def get_video_detail(video_id):
    payload = _request(
        'videos',
        {'part': 'snippet,contentDetails,statistics', 'id': video_id},
    )
    items = payload.get('items', [])
    if not items:
        raise YouTubeAPIError('영상을 찾을 수 없습니다.')
    item = items[0]
    result = _video_from_item(item)
    result['duration'] = (item.get('contentDetails') or {}).get('duration')
    result['statistics'] = item.get('statistics') or {}
    return result
