from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 'supplier', 'created_at')
    list_filter = ('category', 'brand', 'supplier')
    search_fields = ('name', 'sku', 'brand')
