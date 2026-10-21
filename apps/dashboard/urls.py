from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('api/category-chart/', views.api_category_chart, name='api_category_chart'),
    path('api/stock-distribution/', views.api_stock_distribution, name='api_stock_distribution'),
    path('api/monthly-activity/', views.api_monthly_activity, name='api_monthly_activity'),
    path('api/top-products/', views.api_top_products, name='api_top_products'),
]
