from django.urls import path

from .views import (
    CategoryListView,
    CommentDeleteView,
    CommentListCreateView,
    ExpenseLikeToggleView,
    ExpenseLogDetailView,
    ExpenseLogListCreateView,
    FriendExpenseFeedView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('feed/', FriendExpenseFeedView.as_view(), name='friend-expense-feed'),

    path('', ExpenseLogListCreateView.as_view(), name='expense-log-list-create'),
    path('<int:pk>/', ExpenseLogDetailView.as_view(), name='expense-log-detail'),

    path('<int:pk>/like/', ExpenseLikeToggleView.as_view(), name='expense-like-toggle'),
    path('<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]