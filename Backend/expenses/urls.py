from django.urls import path
from . import views
urlpatterns = [
    path('categories/', views.categories),
    path('categories/seed/', views.seed_categories),
    path('logs/', views.logs),
    path('logs/<int:log_id>/', views.log_detail),
    path('feed/', views.friend_feed),
    path('logs/<int:log_id>/like/', views.toggle_like),
    path('logs/<int:log_id>/comments/', views.comments),
]
