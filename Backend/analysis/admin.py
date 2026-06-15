from django.contrib import admin

from .models import AIAnalysis, MonthlyAnalysis


@admin.register(MonthlyAnalysis)
class MonthlyAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'total_amount', 'created_at')
    list_filter = ('year', 'month')


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis', 'status', 'created_at')
    list_filter = ('status',)
