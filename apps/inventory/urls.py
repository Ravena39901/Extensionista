from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('adjust/', views.stock_adjust, name='stock_adjust'),
    path('history/', views.stock_history, name='stock_history'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
]
