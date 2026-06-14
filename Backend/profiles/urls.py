from django.urls import path
from . import views
urlpatterns = [
    path('me/', views.my_profile),
    path('<int:user_id>/', views.profile_detail),
]
