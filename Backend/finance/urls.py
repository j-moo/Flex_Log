from django.urls import path

from . import views


urlpatterns = [
    path('products/', views.product_list, name='finance-product-list'),
    path('products/deposits/', views.deposit_product_list, name='finance-deposit-list'),
    path('products/savings/', views.saving_product_list, name='finance-saving-list'),
    path('products/<int:product_id>/', views.product_detail, name='finance-product-detail'),
    path(
        'subscriptions/',
        views.UserFinancialProductListCreateView.as_view(),
        name='finance-subscription-list-create',
    ),
    path(
        'subscriptions/<int:subscription_id>/cancel/',
        views.cancel_financial_product,
        name='finance-subscription-cancel',
    ),
    path('commodities/', views.commodity_list, name='finance-commodity-list'),
    path(
        'commodities/prices/import/',
        views.import_commodity_prices,
        name='finance-commodity-price-import',
    ),
    path(
        'commodities/<str:code>/prices/',
        views.commodity_price_list,
        name='finance-commodity-price-list',
    ),
    path('youtube/search/', views.youtube_video_search, name='finance-youtube-search'),
    path(
        'youtube/videos/<str:video_id>/',
        views.youtube_video_detail,
        name='finance-youtube-detail',
    ),
    path('banks/nearby/', views.nearby_bank_search, name='finance-nearby-bank-search'),
    path('recommend/', views.recommend_products, name='finance-recommend'),
    path('recommend/latest/', views.latest_recommendations, name='finance-recommend-latest'),
    path('recommend/history/', views.recommendation_history, name='finance-recommend-history'),
    path('quote/', views.stock_quote, name='finance-stock-quote'),
    path('chart/', views.stock_chart, name='finance-stock-chart'),
    path('stocks/', views.StockHoldingListCreateView.as_view(), name='stock-holding-list-create'),
    path('stocks/<int:pk>/', views.StockHoldingDetailView.as_view(), name='stock-holding-detail'),
]
