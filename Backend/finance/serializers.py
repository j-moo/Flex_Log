from rest_framework import serializers

from .models import (
    Commodity,
    CommodityPrice,
    FinancialProduct,
    FinancialProductOption,
    FinancialProductRecommendation,
    StockHolding,
    UserFinancialProduct,
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


class UserFinancialProductSerializer(serializers.ModelSerializer):
    option = FinancialProductOptionSerializer(read_only=True)
    product = FinancialProductSerializer(source='option.product', read_only=True)
    option_id = serializers.PrimaryKeyRelatedField(
        source='option',
        queryset=FinancialProductOption.objects.select_related('product').filter(
            product__is_active=True,
        ),
        write_only=True,
    )

    class Meta:
        model = UserFinancialProduct
        fields = (
            'id',
            'option_id',
            'status',
            'joined_at',
            'cancelled_at',
            'product',
            'option',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'status',
            'joined_at',
            'cancelled_at',
            'product',
            'option',
            'created_at',
            'updated_at',
        )


class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ('code', 'name', 'unit', 'currency', 'created_at')
        read_only_fields = fields


class CommodityPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityPrice
        fields = (
            'price_date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'source',
        )
        read_only_fields = fields


class CommodityPriceImportItemSerializer(serializers.Serializer):
    price_date = serializers.DateField()
    close_price = serializers.DecimalField(max_digits=18, decimal_places=6, min_value=0)
    open_price = serializers.DecimalField(
        max_digits=18, decimal_places=6, min_value=0, required=False, allow_null=True,
    )
    high_price = serializers.DecimalField(
        max_digits=18, decimal_places=6, min_value=0, required=False, allow_null=True,
    )
    low_price = serializers.DecimalField(
        max_digits=18, decimal_places=6, min_value=0, required=False, allow_null=True,
    )
    source = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, attrs):
        high = attrs.get('high_price')
        low = attrs.get('low_price')
        compared = [attrs['close_price']]
        compared.extend(
            value for value in (attrs.get('open_price'), low) if value is not None
        )
        if high is not None and high < max(compared):
            raise serializers.ValidationError('high_price는 다른 가격보다 작을 수 없습니다.')
        compared = [attrs['close_price']]
        compared.extend(
            value for value in (attrs.get('open_price'), high) if value is not None
        )
        if low is not None and low > min(compared):
            raise serializers.ValidationError('low_price는 다른 가격보다 클 수 없습니다.')
        return attrs


class CommodityPriceImportSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=('GOLD', 'SILVER'))
    name = serializers.CharField(max_length=50, required=False)
    unit = serializers.CharField(max_length=30, required=False, default='USD/troy oz')
    currency = serializers.CharField(max_length=3, required=False, default='USD')
    source = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    prices = CommodityPriceImportItemSerializer(many=True, allow_empty=False)

    def validate_currency(self, value):
        return value.upper()

    def validate(self, attrs):
        dates = [item['price_date'] for item in attrs['prices']]
        if len(dates) != len(set(dates)):
            raise serializers.ValidationError({'prices': 'price_date는 요청 안에서 중복될 수 없습니다.'})
        return attrs


class FinancialProductRecommendationSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    analysis_id = serializers.SerializerMethodField()
    option_id = serializers.SerializerMethodField()

    class Meta:
        model = FinancialProductRecommendation
        fields = (
            'id',
            'analysis_id',
            'product_id',
            'option_id',
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

    def get_option_id(self, obj):
        return obj.option_id


class StockHoldingSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    invested_amount = serializers.SerializerMethodField()
    valuation_amount = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    profit_rate = serializers.SerializerMethodField()

    class Meta:
        model = StockHolding
        fields = (
            'id',
            'symbol',
            'name',
            'quantity',
            'average_price',
            'current_price',
            'invested_amount',
            'valuation_amount',
            'profit_loss',
            'profit_rate',
            'memo',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'invested_amount',
            'valuation_amount',
            'profit_loss',
            'profit_rate',
            'created_at',
            'updated_at',
        )

    def get_invested_amount(self, obj):
        return float(round(obj.invested_amount, 2))

    def get_valuation_amount(self, obj):
        return float(round(obj.valuation_amount, 2))

    def get_profit_loss(self, obj):
        return float(round(obj.profit_loss, 2))

    def get_profit_rate(self, obj):
        return float(round(obj.profit_rate, 2))

    def validate_symbol(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        symbol = attrs.get('symbol', getattr(self.instance, 'symbol', '')).strip().upper()
        if self.instance and user and user.is_authenticated:
            queryset = StockHolding.objects.filter(user=user, symbol=symbol)
            queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({'symbol': '\uc774\ubbf8 \ub4f1\ub85d\ub41c \uc885\ubaa9 \ucf54\ub4dc\uc785\ub2c8\ub2e4.'})
        attrs['symbol'] = symbol
        return attrs
