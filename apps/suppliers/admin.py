from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'email', 'phone', 'product_count', 'created_at')
    search_fields = ('supplier_name', 'email')
