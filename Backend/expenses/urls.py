from django.urls import path

from .views import CategoryListView, ExpenseLogDetailView, ExpenseLogListCreateView


urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', ExpenseLogListCreateView.as_view(), name='expense-log-list-create'),
    path('<int:pk>/', ExpenseLogDetailView.as_view(), name='expense-log-detail'),
]
