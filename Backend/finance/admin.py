from django.contrib import admin

from .models import FinancialProduct, ProductRecommendation, StockHolding


@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'product_name', 'product_type', 'base_rate', 'max_rate')
    list_filter = ('product_type', 'bank_name')
    search_fields = ('product_code', 'product_name', 'bank_name')


@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'priority', 'created_at')


@admin.register(StockHolding)
class StockHoldingAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock_symbol', 'stock_name', 'quantity', 'average_price')
    search_fields = ('user__username', 'stock_symbol', 'stock_name')
