"""
URL configuration for fashion_inventory_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('products/', include('apps.products.urls')),
    path('categories/', include('apps.categories.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('inventory/', include('apps.inventory.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
