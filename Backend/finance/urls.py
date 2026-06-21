from django.urls import path

from . import views


urlpatterns = [
    path('products/', views.product_list, name='finance-product-list'),
    path('products/deposits/', views.deposit_product_list, name='finance-deposit-list'),
    path('products/savings/', views.saving_product_list, name='finance-saving-list'),
    path('products/<int:product_id>/', views.product_detail, name='finance-product-detail'),
    path('recommend/', views.recommend_products, name='finance-recommend'),
    path('recommend/latest/', views.latest_recommendations, name='finance-recommend-latest'),
    path('recommend/history/', views.recommendation_history, name='finance-recommend-history'),
    path('quote/', views.stock_quote, name='finance-stock-quote'),
    path('chart/', views.stock_chart, name='finance-stock-chart'),
    path('stocks/', views.StockHoldingListCreateView.as_view(), name='stock-holding-list-create'),
    path('stocks/<int:pk>/', views.StockHoldingDetailView.as_view(), name='stock-holding-detail'),
]
