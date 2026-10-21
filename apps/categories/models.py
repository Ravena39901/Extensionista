from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['category_name']

    def __str__(self):
        return self.category_name

    @property
    def product_count(self):
        return self.products.count()
