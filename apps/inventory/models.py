from django.db import models


class StockLog(models.Model):
    CHANGE_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='stock_logs'
    )
    change_type = models.CharField(max_length=3, choices=CHANGE_TYPES)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_change_type_display()} - {self.product.name} ({self.quantity})"
