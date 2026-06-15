from django.urls import path

from .views import (
    FriendListCreateView,
    FriendUpdateView,
    UserSearchView,
)

urlpatterns = [
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('', FriendListCreateView.as_view(), name='friend-list-create'),
    path('<int:pk>/', FriendUpdateView.as_view(), name='friend-update'),
]