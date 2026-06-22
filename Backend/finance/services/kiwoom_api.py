import re
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone

from .kiwoom_auth import KiwoomAPIError, get_access_token


QUOTE_API_ID = 'ka10001'
MINUTE_CHART_API_ID = 'ka10080'
DAILY_CHART_API_ID = 'ka10081'
STOCK_ENDPOINT = '/api/dostk/stkinfo'

MINUTE_PERIODS = {
    '1m': '1',
    '3m': '3',
    '5m': '5',
    '10m': '10',
    '15m': '15',
    '30m': '30',
    '60m': '60',
}
DAILY_PERIODS = {'1d', 'day', 'daily', 'd'}


def _clean_symbol(symbol):
    symbol = str(symbol or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9]{6,12}', symbol):
        raise KiwoomAPIError('symbol must be a 6-12 character stock code.')
    return symbol.upper()


def _clean_number(value, absolute=False):
    if value is None:
        return None
    cleaned = str(value).strip().replace(',', '').replace('%', '')
    if cleaned == '':
        return None
    try:
        number = float(cleaned)
    except ValueError:
        return None
    if absolute:
        number = abs(number)
    if number.is_integer():
        return int(number)
    return number


def _first_value(data, keys):
    for key in keys:
        value = data.get(key)
        if value not in (None, ''):
            return value
    return None


def _build_url(path):
    return f'{settings.KIWOOM_BASE_URL.rstrip("/")}/{path.lstrip("/")}'


def _request(api_id, body, retry=True):
    token = get_access_token()
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'authorization': f'Bearer {token}',
        'cont-yn': 'N',
        'next-key': '',
        'api-id': api_id,
    }

    try:
        response = requests.post(
            _build_url(STOCK_ENDPOINT),
            json=body,
            headers=headers,
            timeout=settings.KIWOOM_REQUEST_TIMEOUT,
        )
        if response.status_code == 401 and retry:
            get_access_token(force_refresh=True)
            return _request(api_id, body, retry=False)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise KiwoomAPIError(f'Kiwoom API request failed: {exc}') from exc
    except ValueError as exc:
        raise KiwoomAPIError('Kiwoom API response was not valid JSON.') from exc

    return_code = str(payload.get('return_code') or payload.get('rt_cd') or '').strip()
    if return_code and return_code not in {'0', '0000'}:
        message = payload.get('return_msg') or payload.get('msg1') or 'Unknown Kiwoom API error.'
        raise KiwoomAPIError(f'Kiwoom API error({return_code}): {message}')

    return payload


def get_quote(symbol):
    symbol = _clean_symbol(symbol)
    payload = _request(QUOTE_API_ID, {'stk_cd': symbol})

    current_price = _clean_number(
        _first_value(payload, ('cur_prc', 'stck_prpr', 'current_price', 'price')),
        absolute=True,
    )
    if current_price is None:
        raise KiwoomAPIError('Current price was not returned from Kiwoom.')

    return {
        'symbol': symbol,
        'name': _first_value(payload, ('stk_nm', 'hts_kor_isnm', 'name')) or '',
        'current_price': current_price,
        'change_rate': _clean_number(_first_value(payload, ('flu_rt', 'prdy_ctrt', 'change_rate'))),
        'change_price': _clean_number(_first_value(payload, ('pred_pre', 'prdy_vrss', 'change_price'))),
    }


def _parse_chart_time(value, period):
    raw_value = str(value or '').strip()
    if not raw_value:
        return None

    current_tz = timezone.get_current_timezone()
    formats = ['%Y%m%d%H%M%S', '%Y%m%d%H%M', '%Y%m%d']
    if period in MINUTE_PERIODS:
        today = timezone.localtime(timezone.now()).strftime('%Y%m%d')
        formats.extend(['%H%M%S', '%H%M'])
        if len(raw_value) in {4, 6}:
            raw_value = f'{today}{raw_value}'

    for fmt in formats:
        try:
            parsed = datetime.strptime(raw_value, fmt)
            return timezone.make_aware(parsed, current_tz).replace(tzinfo=None).isoformat()
        except ValueError:
            continue
    return raw_value


def _extract_chart_rows(payload):
    for key in (
        'stk_min_pole_chart_qry',
        'stk_dt_pole_chart_qry',
        'output',
        'output1',
        'chart',
        'data',
    ):
        rows = payload.get(key)
        if isinstance(rows, list):
            return rows
    if isinstance(payload, list):
        return payload
    return []


def get_chart(symbol, period='1m'):
    symbol = _clean_symbol(symbol)
    period = str(period or '1m').lower()

    if period in MINUTE_PERIODS:
        payload = _request(
            MINUTE_CHART_API_ID,
            {
                'stk_cd': symbol,
                'tic_scope': MINUTE_PERIODS[period],
                'upd_stkpc_tp': '1',
            },
        )
    elif period in DAILY_PERIODS:
        payload = _request(
            DAILY_CHART_API_ID,
            {
                'stk_cd': symbol,
                'base_dt': timezone.localtime(timezone.now()).strftime('%Y%m%d'),
                'upd_stkpc_tp': '1',
            },
        )
    else:
        supported_periods = ', '.join(sorted([*MINUTE_PERIODS.keys(), '1d']))
        raise KiwoomAPIError(f'Unsupported period. Supported periods: {supported_periods}')

    points = []
    for row in _extract_chart_rows(payload):
        if not isinstance(row, dict):
            continue
        raw_time = _first_value(row, ('cntr_tm', 'stck_bsop_date', 'dt', 'date', 'time'))
        price = _clean_number(
            _first_value(row, ('cur_prc', 'stck_prpr', 'close_pric', 'price')),
            absolute=True,
        )
        parsed_time = _parse_chart_time(raw_time, period)
        if parsed_time and price is not None:
            points.append({'time': parsed_time, 'price': price})

    return sorted(points, key=lambda point: point['time'])
