from rest_framework import serializers

from .models import (
    FinancialProduct,
    FinancialProductOption,
    FinancialProductRecommendation,
)


class FinancialProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProductOption
        fields = (
            'id',
            'intr_rate_type',
            'intr_rate_type_nm',
            'save_trm',
            'intr_rate',
            'intr_rate2',
            'rsrv_type',
            'rsrv_type_nm',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class FinancialProductSerializer(serializers.ModelSerializer):
    options = FinancialProductOptionSerializer(many=True, read_only=True)
    best_rate = serializers.SerializerMethodField()
    best_option = serializers.SerializerMethodField()

    class Meta:
        model = FinancialProduct
        fields = (
            'id',
            'product_type',
            'fin_prdt_cd',
            'dcls_month',
            'kor_co_nm',
            'fin_prdt_nm',
            'join_way',
            'mtrt_int',
            'spcl_cnd',
            'join_deny',
            'join_member',
            'etc_note',
            'max_limit',
            'is_active',
            'fetched_at',
            'created_at',
            'best_rate',
            'best_option',
            'options',
        )
        read_only_fields = fields

    def get_best_rate(self, obj):
        option = self._get_best_option(obj)
        if not option:
            return None
        return option.intr_rate2 if option.intr_rate2 is not None else option.intr_rate

    def get_best_option(self, obj):
        option = self._get_best_option(obj)
        if not option:
            return None
        return FinancialProductOptionSerializer(option).data

    def _get_best_option(self, obj):
        options = list(getattr(obj, 'options').all())
        if not options:
            return None
        return max(
            options,
            key=lambda option: (
                option.intr_rate2 if option.intr_rate2 is not None else option.intr_rate or 0,
                option.intr_rate or 0,
            ),
        )


class FinancialProductRecommendationSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    analysis_id = serializers.SerializerMethodField()

    class Meta:
        model = FinancialProductRecommendation
        fields = (
            'id',
            'analysis_id',
            'product_id',
            'title',
            'description',
            'reason',
            'action_text',
            'bank_name',
            'product_name',
            'product_type',
            'save_trm',
            'interest_rate',
            'max_interest_rate',
            'ai_comment',
            'caution',
            'priority',
            'created_at',
        )
        read_only_fields = fields

    def get_product_id(self, obj):
        return obj.product_id

    def get_analysis_id(self, obj):
        return obj.analysis_id
