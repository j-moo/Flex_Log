from django.urls import path
from . import views
urlpatterns = [
    path('monthly/', views.monthly_list),
    path('monthly/create/', views.create_monthly_analysis),
    path('ai/', views.ai_list),
    path('ai/create/', views.create_ai_analysis),
]
