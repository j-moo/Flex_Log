import json
from pathlib import Path

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone


PRODUCT_ENDPOINTS = {
    'deposit': 'depositProductsSearch.json',
    'saving': 'savingProductsSearch.json',
}
PRODUCT_TYPE_ORDER = {
    'deposit': 1,
    'saving': 2,
}


class FinLifeAPIError(Exception):
    pass


def clean_text(value):
    if value is None:
        return ''
    return str(value).strip()


def to_int(value):
    value = clean_text(value).replace(',', '')
    if value == '':
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def to_float(value):
    value = clean_text(value).replace(',', '')
    if value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def term_sort_value(value):
    numeric_value = to_int(value)
    if numeric_value is None:
        return 9999
    return numeric_value


def normalize_product(product_type, item):
    return {
        'product_type': product_type,
        'fin_prdt_cd': clean_text(item.get('fin_prdt_cd')),
        'dcls_month': clean_text(item.get('dcls_month')),
        'kor_co_nm': clean_text(item.get('kor_co_nm')),
        'fin_prdt_nm': clean_text(item.get('fin_prdt_nm')),
        'join_way': clean_text(item.get('join_way')),
        'mtrt_int': clean_text(item.get('mtrt_int')),
        'spcl_cnd': clean_text(item.get('spcl_cnd')),
        'join_deny': clean_text(item.get('join_deny')),
        'join_member': clean_text(item.get('join_member')),
        'etc_note': clean_text(item.get('etc_note')),
        'max_limit': to_int(item.get('max_limit')),
        'is_active': True,
    }


def normalize_option(product_type, item):
    return {
        'product_type': product_type,
        'fin_prdt_cd': clean_text(item.get('fin_prdt_cd')),
        'intr_rate_type': clean_text(item.get('intr_rate_type')),
        'intr_rate_type_nm': clean_text(item.get('intr_rate_type_nm')),
        'save_trm': clean_text(item.get('save_trm')),
        'intr_rate': to_float(item.get('intr_rate')),
        'intr_rate2': to_float(item.get('intr_rate2')),
        'rsrv_type': clean_text(item.get('rsrv_type')),
        'rsrv_type_nm': clean_text(item.get('rsrv_type_nm')),
    }


def get_product_types(product_type):
    if product_type == 'all':
        return ['deposit', 'saving']
    if product_type not in PRODUCT_ENDPOINTS:
        raise FinLifeAPIError(f'Unsupported product type: {product_type}')
    return [product_type]


def fetch_finlife_page(product_type, page_no=1):
    if not settings.FINLIFE_API_KEY:
        raise FinLifeAPIError('[ERROR] api_key is missing. Please check backend/.env')

    endpoint = PRODUCT_ENDPOINTS.get(product_type)
    if not endpoint:
        raise FinLifeAPIError(f'Unsupported product type: {product_type}')

    base_url = settings.FINLIFE_API_BASE_URL.rstrip('/')
    params = {
        'auth': settings.FINLIFE_API_KEY,
        'topFinGrpNo': settings.FINLIFE_TOP_FIN_GRP_NO,
        'pageNo': page_no,
    }

    try:
        response = requests.get(
            f'{base_url}/{endpoint}',
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise FinLifeAPIError(f'FinLife API request failed: {exc}') from exc
    except ValueError as exc:
        raise FinLifeAPIError('FinLife API returned invalid JSON.') from exc

    result = payload.get('result') or {}
    err_cd = clean_text(result.get('err_cd'))
    if err_cd and err_cd != '000':
        err_msg = clean_text(result.get('err_msg')) or 'Unknown FinLife API error.'
        raise FinLifeAPIError(f'FinLife API error({err_cd}): {err_msg}')

    return {
        'base_list': result.get('baseList') or [],
        'option_list': result.get('optionList') or [],
        'max_page_no': to_int(result.get('max_page_no')) or page_no,
    }


def fetch_finlife_products(product_type):
    page_no = 1
    max_page_no = 1
    base_list = []
    option_list = []

    while page_no <= max_page_no:
        page = fetch_finlife_page(product_type, page_no)
        base_list.extend(page['base_list'])
        option_list.extend(page['option_list'])
        max_page_no = page['max_page_no']
        page_no += 1

    return {
        'base_list': base_list,
        'option_list': option_list,
    }


def fetch_selected_products(product_type='all'):
    datasets = {}
    for selected_type in get_product_types(product_type):
        datasets[selected_type] = fetch_finlife_products(selected_type)
    return datasets


def build_fixture_objects(datasets):
    timestamp = timezone.now().replace(microsecond=0).isoformat()
    product_map = {}
    option_map = {}

    for product_type in sorted(datasets, key=lambda value: PRODUCT_TYPE_ORDER.get(value, 99)):
        dataset = datasets[product_type]
        for item in dataset.get('base_list', []):
            product = normalize_product(product_type, item)
            if not product['fin_prdt_cd']:
                continue
            key = (product_type, product['fin_prdt_cd'])
            current = product_map.get(key)
            if current and current.get('dcls_month', '') > product.get('dcls_month', ''):
                continue
            product_map[key] = product

        for item in dataset.get('option_list', []):
            option = normalize_option(product_type, item)
            if not option['fin_prdt_cd']:
                continue
            product_key = (product_type, option['fin_prdt_cd'])
            key = (
                product_key,
                option['save_trm'],
                option['intr_rate_type'],
                option['rsrv_type'],
            )
            current = option_map.get(key)
            current_rate = max(
                current.get('intr_rate2') or 0,
                current.get('intr_rate') or 0,
            ) if current else -1
            new_rate = max(option.get('intr_rate2') or 0, option.get('intr_rate') or 0)
            if current and current_rate > new_rate:
                continue
            option_map[key] = option

    fixture = []
    product_pk_map = {}
    product_items = sorted(
        product_map.items(),
        key=lambda item: (
            PRODUCT_TYPE_ORDER.get(item[0][0], 99),
            item[1]['kor_co_nm'],
            item[1]['fin_prdt_nm'],
            item[1]['fin_prdt_cd'],
        ),
    )

    for pk, (key, fields) in enumerate(product_items, start=1):
        product_pk_map[key] = pk
        fixture_fields = fields.copy()
        fixture_fields['fetched_at'] = timestamp
        fixture_fields['created_at'] = timestamp
        fixture.append(
            {
                'model': 'finance.financialproduct',
                'pk': pk,
                'fields': fixture_fields,
            }
        )

    option_items = sorted(
        option_map.items(),
        key=lambda item: (
            product_pk_map.get(item[0][0], 999999),
            term_sort_value(item[1]['save_trm']),
            item[1]['save_trm'],
            item[1]['intr_rate_type'],
            item[1]['rsrv_type'],
        ),
    )

    option_pk = 1
    for key, fields in option_items:
        product_key = key[0]
        product_pk = product_pk_map.get(product_key)
        if not product_pk:
            continue

        fixture_fields = {
            'product': product_pk,
            'intr_rate_type': fields['intr_rate_type'],
            'intr_rate_type_nm': fields['intr_rate_type_nm'],
            'save_trm': fields['save_trm'],
            'intr_rate': fields['intr_rate'],
            'intr_rate2': fields['intr_rate2'],
            'rsrv_type': fields['rsrv_type'],
            'rsrv_type_nm': fields['rsrv_type_nm'],
            'created_at': timestamp,
            'updated_at': timestamp,
        }
        fixture.append(
            {
                'model': 'finance.financialproductoption',
                'pk': option_pk,
                'fields': fixture_fields,
            }
        )
        option_pk += 1

    return fixture


def write_fixture_file(fixture_objects, output_path=None):
    if output_path is None:
        fixture_dir = Path(__file__).resolve().parent / 'fixtures'
        output_path = fixture_dir / 'financial_products.json'
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as fixture_file:
        json.dump(fixture_objects, fixture_file, ensure_ascii=False, indent=2)
        fixture_file.write('\n')
    return output_path


@transaction.atomic
def save_products_to_db(datasets):
    from .models import FinancialProduct, FinancialProductOption

    saved_product_ids = []
    saved_option_ids = []
    product_by_key = {}

    for product_type in sorted(datasets, key=lambda value: PRODUCT_TYPE_ORDER.get(value, 99)):
        dataset = datasets[product_type]
        for item in dataset.get('base_list', []):
            fields = normalize_product(product_type, item)
            fin_prdt_cd = fields.pop('fin_prdt_cd')
            if not fin_prdt_cd:
                continue
            product, _ = FinancialProduct.objects.update_or_create(
                product_type=product_type,
                fin_prdt_cd=fin_prdt_cd,
                defaults=fields,
            )
            saved_product_ids.append(product.id)
            product_by_key[(product_type, fin_prdt_cd)] = product

    for product_type in sorted(datasets, key=lambda value: PRODUCT_TYPE_ORDER.get(value, 99)):
        dataset = datasets[product_type]
        for item in dataset.get('option_list', []):
            fields = normalize_option(product_type, item)
            fin_prdt_cd = fields.pop('fin_prdt_cd')
            fields.pop('product_type', None)
            product = product_by_key.get((product_type, fin_prdt_cd))
            if not product:
                continue
            option, _ = FinancialProductOption.objects.update_or_create(
                product=product,
                save_trm=fields['save_trm'],
                intr_rate_type=fields['intr_rate_type'],
                rsrv_type=fields['rsrv_type'],
                defaults=fields,
            )
            saved_option_ids.append(option.id)

    selected_types = list(datasets.keys())
    FinancialProduct.objects.filter(product_type__in=selected_types).exclude(
        id__in=saved_product_ids,
    ).update(is_active=False)
    FinancialProductOption.objects.filter(product__product_type__in=selected_types).exclude(
        id__in=saved_option_ids,
    ).delete()

    return {
        'products': len(saved_product_ids),
        'options': len(saved_option_ids),
    }
