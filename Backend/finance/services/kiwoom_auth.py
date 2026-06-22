from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


TOKEN_CACHE_KEY = 'kiwoom_access_token'
DEFAULT_TOKEN_TTL_SECONDS = 23 * 60 * 60


class KiwoomAPIError(Exception):
    pass


def _build_url(path):
    return f'{settings.KIWOOM_BASE_URL.rstrip("/")}/{path.lstrip("/")}'


def _parse_expires_at(payload):
    expires_in = payload.get('expires_in')
    if expires_in:
        try:
            return timezone.now() + timedelta(seconds=max(int(expires_in) - 60, 60))
        except (TypeError, ValueError):
            pass

    expires_dt = payload.get('expires_dt') or payload.get('expires_at')
    if expires_dt:
        for fmt in ('%Y%m%d%H%M%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
            try:
                parsed = datetime.strptime(str(expires_dt), fmt)
                return timezone.make_aware(parsed, timezone.get_current_timezone())
            except ValueError:
                continue

    return timezone.now() + timedelta(seconds=DEFAULT_TOKEN_TTL_SECONDS)


def _token_ttl(expires_at):
    seconds = int((expires_at - timezone.now()).total_seconds()) - 60
    return max(seconds, 60)


def get_access_token(force_refresh=False):
    if not force_refresh:
        cached_token = cache.get(TOKEN_CACHE_KEY)
        if cached_token:
            return cached_token

    if not settings.KIWOOM_APP_KEY or not settings.KIWOOM_SECRET_KEY:
        raise KiwoomAPIError('KIWOOM_APP_KEY and KIWOOM_SECRET_KEY are required.')

    try:
        response = requests.post(
            _build_url(settings.KIWOOM_TOKEN_PATH),
            json={
                'grant_type': 'client_credentials',
                'appkey': settings.KIWOOM_APP_KEY,
                'secretkey': settings.KIWOOM_SECRET_KEY,
            },
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            timeout=settings.KIWOOM_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise KiwoomAPIError(f'Kiwoom token request failed: {exc}') from exc
    except ValueError as exc:
        raise KiwoomAPIError('Kiwoom token response was not valid JSON.') from exc

    token = payload.get('token') or payload.get('access_token')
    if not token:
        message = payload.get('return_msg') or payload.get('message') or 'Access token was not returned.'
        raise KiwoomAPIError(f'Kiwoom token error: {message}')

    expires_at = _parse_expires_at(payload)
    cache.set(TOKEN_CACHE_KEY, token, _token_ttl(expires_at))
    return token
