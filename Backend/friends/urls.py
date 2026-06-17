from django.urls import path

from .views import FriendDetailView, FriendListCreateView, UserSearchView


urlpatterns = [
    path('users/', UserSearchView.as_view(), name='friend-user-search'),
    path('', FriendListCreateView.as_view(), name='friend-list-create'),
    path('<int:pk>/', FriendDetailView.as_view(), name='friend-detail'),
]
