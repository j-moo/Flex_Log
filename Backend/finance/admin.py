from django.contrib import admin

from .models import (
    Commodity,
    CommodityPrice,
    FinancialProduct,
    FinancialProductOption,
    FinancialProductRecommendation,
    StockHolding,
    UserFinancialProduct,
)


class FinancialProductOptionInline(admin.TabularInline):
    model = FinancialProductOption
    extra = 0


@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display = (
        'kor_co_nm',
        'fin_prdt_nm',
        'product_type',
        'fin_prdt_cd',
        'is_active',
    )
    list_filter = ('product_type', 'is_active', 'kor_co_nm')
    search_fields = ('kor_co_nm', 'fin_prdt_nm', 'fin_prdt_cd')
    inlines = (FinancialProductOptionInline,)


@admin.register(FinancialProductRecommendation)
class FinancialProductRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'bank_name',
        'product_name',
        'priority',
        'created_at',
    )
    list_filter = ('product_type', 'created_at')
    search_fields = ('user__username', 'bank_name', 'product_name', 'title')


admin.site.register(UserFinancialProduct)
admin.site.register(Commodity)
admin.site.register(CommodityPrice)
admin.site.register(StockHolding)
