from django.urls import path

from . import views


urlpatterns = [
    path('monthly/', views.monthly_analysis, name='monthly-analysis'),
    path('monthly/latest/', views.latest_monthly_analysis, name='latest-monthly-analysis'),
    path('monthly/history/', views.monthly_analysis_history, name='monthly-analysis-history'),
]
