from django.apps import apps
from django.test import SimpleTestCase


class FinanceMvpScopeTests(SimpleTestCase):
    def test_finance_models_are_excluded_from_current_mvp(self):
        finance_models = list(apps.get_app_config('finance').get_models())

        self.assertEqual(finance_models, [])
