from django.core.management.base import BaseCommand

from finance.finlife import (
    FinLifeAPIError,
    build_fixture_objects,
    fetch_selected_products,
    write_fixture_file,
)


class Command(BaseCommand):
    help = 'Fetch FinLife deposit/saving products and create a Django fixture.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['all', 'deposit', 'saving'],
            default='all',
            help='Product type to fetch. Default: all',
        )

    def handle(self, *args, **options):
        product_type = options['type']
        self.stdout.write('[START] Fetching FinLife products...')

        try:
            datasets = fetch_selected_products(product_type)
        except FinLifeAPIError as exc:
            self.stdout.write(str(exc))
            return

        if 'deposit' in datasets:
            self.stdout.write(
                f"[OK] Deposit products fetched: {len(datasets['deposit']['base_list'])}"
            )
            self.stdout.write(
                f"[OK] Deposit options fetched: {len(datasets['deposit']['option_list'])}"
            )
        if 'saving' in datasets:
            self.stdout.write(
                f"[OK] Saving products fetched: {len(datasets['saving']['base_list'])}"
            )
            self.stdout.write(
                f"[OK] Saving options fetched: {len(datasets['saving']['option_list'])}"
            )

        fixture_objects = build_fixture_objects(datasets)
        output_path = write_fixture_file(fixture_objects)
        display_path = output_path.relative_to(output_path.parents[2])
        self.stdout.write(f'[OK] Fixture created: {display_path.as_posix()}')
        self.stdout.write(
            '[DONE] You can load data with: python manage.py loaddata financial_products.json'
        )
