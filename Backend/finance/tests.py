from django.apps import apps
from django.test import SimpleTestCase


class FinanceModelRegistrationTests(SimpleTestCase):
    def test_finance_models_are_registered(self):
        model_names = {
            model.__name__
            for model in apps.get_app_config('finance').get_models()
        }

        self.assertIn('FinancialProduct', model_names)
        self.assertIn('FinancialProductOption', model_names)
        self.assertIn('FinancialProductRecommendation', model_names)
