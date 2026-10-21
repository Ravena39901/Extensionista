from django.contrib import admin
from .models import StockLog


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_type', 'quantity', 'created_at')
    list_filter = ('change_type',)
    search_fields = ('product__name',)
