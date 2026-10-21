from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        'categories.Category', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    brand = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity < 10

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0
