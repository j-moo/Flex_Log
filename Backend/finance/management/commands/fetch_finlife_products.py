from django.core.management.base import BaseCommand

from finance.finlife import FinLifeAPIError, fetch_selected_products, save_products_to_db


class Command(BaseCommand):
    help = 'Fetch FinLife deposit/saving products and save them to the current database.'

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
            result = save_products_to_db(datasets)
        except FinLifeAPIError as exc:
            self.stdout.write(str(exc))
            return

        self.stdout.write(f"[OK] Products saved: {result['products']}")
        self.stdout.write(f"[OK] Options saved: {result['options']}")
        self.stdout.write('[DONE] FinLife products are stored in the database.')
