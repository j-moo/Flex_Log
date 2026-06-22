import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.db import transaction

from .models import Commodity, CommodityPrice


DATA_DIR = Path(__file__).resolve().parent / 'data'
DATASETS = {
    'GOLD': {
        'filename': 'Gold_prices.json',
        'root_key': 'Gold',
        'name': '금',
    },
    'SILVER': {
        'filename': 'Silver_prices.json',
        'root_key': 'Silver',
        'name': '은',
    },
}


def parse_price(value):
    if value is None or value == '':
        return None
    try:
        parsed = Decimal(str(value).replace(',', '').strip())
    except (InvalidOperation, AttributeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def load_dataset(code):
    metadata = DATASETS[code]
    path = DATA_DIR / metadata['filename']
    with path.open(encoding='utf-8-sig') as data_file:
        payload = json.load(data_file)
    rows = payload.get(metadata['root_key'])
    if not isinstance(rows, list):
        raise ValueError(f'{path.name}에 {metadata["root_key"]} 배열이 없습니다.')
    return metadata, rows


@transaction.atomic
def import_commodity_dataset(code):
    metadata, rows = load_dataset(code)
    commodity, _ = Commodity.objects.update_or_create(
        code=code,
        defaults={
            'name': metadata['name'],
            'unit': 'USD/troy oz',
            'currency': 'USD',
        },
    )

    created_count = 0
    updated_count = 0
    skipped_count = 0
    for row in rows:
        try:
            price_date = date.fromisoformat(str(row.get('Date', '')).strip())
        except ValueError:
            skipped_count += 1
            continue
        close_price = parse_price(row.get('Close/Last'))
        if close_price is None:
            skipped_count += 1
            continue

        _, created = CommodityPrice.objects.update_or_create(
            commodity=commodity,
            price_date=price_date,
            defaults={
                'close_price': close_price,
                'open_price': parse_price(row.get('Open')),
                'high_price': parse_price(row.get('High')),
                'low_price': parse_price(row.get('Low')),
                'source': metadata['filename'],
            },
        )
        created_count += int(created)
        updated_count += int(not created)

    return {
        'code': code,
        'created': created_count,
        'updated': updated_count,
        'skipped': skipped_count,
    }


def import_all_commodity_datasets():
    return [import_commodity_dataset(code) for code in DATASETS]
