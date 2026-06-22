import json

from django.core.management.base import BaseCommand, CommandError

from finance.commodity_data import DATASETS, import_commodity_dataset


class Command(BaseCommand):
    help = 'finance/data의 금·은 JSON 시세를 DB에 업서트합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commodity',
            choices=('all', *DATASETS.keys()),
            default='all',
        )

    def handle(self, *args, **options):
        codes = DATASETS.keys() if options['commodity'] == 'all' else (options['commodity'],)
        try:
            results = [import_commodity_dataset(code) for code in codes]
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise CommandError(str(exc)) from exc

        for result in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{result['code']}: 생성 {result['created']} / "
                    f"갱신 {result['updated']} / 제외 {result['skipped']}"
                )
            )
