from rest_framework import serializers

from .models import MonthlyAIAnalysis, MonthlyAnalysis


class MonthlyAnalysisSerializer(serializers.ModelSerializer):
    category_items = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyAnalysis
        fields = (
            'id',
            'year',
            'month',
            'total_amount',
            'category_summary',
            'category_items',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_category_items(self, obj):
        total = obj.total_amount or 0
        items = []
        for name, amount in obj.category_summary.items():
            numeric_amount = int(amount or 0)
            items.append(
                {
                    'name': name,
                    'amount': numeric_amount,
                    'ratio': round((numeric_amount / total) * 100, 1) if total else 0,
                }
            )
        return sorted(items, key=lambda item: item['amount'], reverse=True)


class MonthlyAIAnalysisRequestSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=2100)
    month = serializers.IntegerField(min_value=1, max_value=12)
    monthly_income = serializers.IntegerField(min_value=0, required=False, default=0)


class MonthlyAIAnalysisSerializer(serializers.ModelSerializer):
    category_items = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyAIAnalysis
        fields = (
            'id',
            'year',
            'month',
            'total_amount',
            'log_count',
            'average_amount',
            'category_summary',
            'category_items',
            'summary',
            'problem',
            'feedback',
            'saving_tip',
            'risk_level',
            'created_at',
        )
        read_only_fields = fields

    def get_category_items(self, obj):
        total = obj.total_amount or 0
        items = []
        for name, values in obj.category_summary.items():
            category_total = int(values.get('total', 0) or 0)
            items.append(
                {
                    'name': name,
                    'total': category_total,
                    'count': int(values.get('count', 0) or 0),
                    'ratio': round((category_total / total) * 100, 1) if total else 0,
                }
            )
        return sorted(items, key=lambda item: item['total'], reverse=True)
