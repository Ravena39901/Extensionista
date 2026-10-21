from django.db import models


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['supplier_name']

    def __str__(self):
        return self.supplier_name

    @property
    def product_count(self):
        return self.products.count()
