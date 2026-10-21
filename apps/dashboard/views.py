from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta

from apps.products.models import Product
from apps.categories.models import Category
from apps.suppliers.models import Supplier
from apps.inventory.models import StockLog


def dashboard_view(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    low_stock = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lt=10).count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()

    total_value = Product.objects.aggregate(
        total=Sum(F('price') * F('stock_quantity'))
    )['total'] or 0

    recent_products = Product.objects.select_related('category', 'supplier')[:10]
    recent_logs = StockLog.objects.select_related('product')[:10]
    low_stock_products = Product.objects.filter(
        stock_quantity__gt=0, stock_quantity__lt=10
    ).select_related('category')[:10]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_value': total_value,
        'recent_products': recent_products,
        'recent_logs': recent_logs,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboard/dashboard.html', context)


def api_category_chart(request):
    """JSON data for products-by-category chart."""
    data = Category.objects.annotate(
        count=Count('products')
    ).values('category_name', 'count').order_by('-count')
    labels = [d['category_name'] for d in data]
    values = [d['count'] for d in data]
    return JsonResponse({'labels': labels, 'values': values})


def api_stock_distribution(request):
    """JSON data for stock distribution chart."""
    in_stock = Product.objects.filter(stock_quantity__gte=10).count()
    low = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lt=10).count()
    out = Product.objects.filter(stock_quantity=0).count()
    return JsonResponse({
        'labels': ['In Stock (≥10)', 'Low Stock (1-9)', 'Out of Stock'],
        'values': [in_stock, low, out],
    })


def api_monthly_activity(request):
    """JSON data for monthly inventory activity chart."""
    today = timezone.now()
    labels = []
    stock_in = []
    stock_out = []
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30 * i)).replace(day=1)
        if i > 0:
            month_end = (today - timedelta(days=30 * (i - 1))).replace(day=1)
        else:
            month_end = today + timedelta(days=1)
        labels.append(month_start.strftime('%b %Y'))
        sin = StockLog.objects.filter(
            change_type='IN', created_at__gte=month_start, created_at__lt=month_end
        ).aggregate(total=Sum('quantity'))['total'] or 0
        sout = StockLog.objects.filter(
            change_type='OUT', created_at__gte=month_start, created_at__lt=month_end
        ).aggregate(total=Sum('quantity'))['total'] or 0
        stock_in.append(sin)
        stock_out.append(sout)
    return JsonResponse({'labels': labels, 'stock_in': stock_in, 'stock_out': stock_out})


def api_top_products(request):
    """JSON data for top products by stock value."""
    products = Product.objects.annotate(
        value=F('price') * F('stock_quantity')
    ).order_by('-value')[:8]
    labels = [p.name[:20] for p in products]
    values = [float(p.value) if p.value else 0 for p in products]
    return JsonResponse({'labels': labels, 'values': values})
