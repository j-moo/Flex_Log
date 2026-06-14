from django.urls import path
from . import views
urlpatterns = [
    path('search/', views.user_search),
    path('request/', views.request_friend),
    path('requests/received/', views.received_requests),
    path('requests/<int:friend_id>/respond/', views.respond_request),
    path('', views.friend_list),
]
