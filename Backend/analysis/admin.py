from django.contrib import admin

from .models import MonthlyAIAnalysis, MonthlyAnalysis


@admin.register(MonthlyAnalysis)
class MonthlyAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'total_amount', 'created_at')
    list_filter = ('year', 'month')
    search_fields = ('user__username',)


@admin.register(MonthlyAIAnalysis)
class MonthlyAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'total_amount', 'risk_level', 'created_at')
    list_filter = ('year', 'month', 'risk_level')
    search_fields = ('user__username', 'summary', 'feedback')
