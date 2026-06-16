from django.urls import path

from .views import (
    CategoryListView,
    CommentDetailView,
    CommentListCreateView,
    ExpenseLogDetailView,
    ExpenseLogListCreateView,
    FriendFeedListView,
    LikeToggleView,
)


urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('feed/', FriendFeedListView.as_view(), name='friend-feed'),
    path('', ExpenseLogListCreateView.as_view(), name='expense-log-list-create'),
    path('<int:pk>/', ExpenseLogDetailView.as_view(), name='expense-log-detail'),
    path('<int:pk>/like/', LikeToggleView.as_view(), name='expense-log-like'),
    path('<int:pk>/comments/', CommentListCreateView.as_view(), name='expense-log-comments'),
    path(
        '<int:pk>/comments/<int:comment_pk>/',
        CommentDetailView.as_view(),
        name='expense-log-comment-detail',
    ),
]
