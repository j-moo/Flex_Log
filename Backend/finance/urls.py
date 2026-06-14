from django.urls import path
from . import views
urlpatterns = [
    path('products/', views.products),
    path('products/seed/', views.seed_products),
    path('recommendations/', views.recommendations),
    path('recommendations/create/', views.create_recommendations),
]
