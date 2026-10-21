from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator

from apps.products.models import Product
from apps.categories.models import Category
from apps.suppliers.models import Supplier
from .models import StockLog
from .forms import StockAdjustForm


def inventory_list(request):
    products = Product.objects.select_related('category', 'supplier').all()

    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )

    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)

    paginator = Paginator(products, 15)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'products': products,
        'query': query,
        'stock_filter': stock_filter,
    }
    return render(request, 'inventory/inventory_list.html', context)


def stock_adjust(request):
    if request.method == 'POST':
        form = StockAdjustForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            change_type = form.cleaned_data['change_type']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']

            if change_type == 'IN':
                product.stock_quantity += quantity
            else:
                if product.stock_quantity >= quantity:
                    product.stock_quantity -= quantity
                else:
                    messages.error(request, f'Cannot remove {quantity} units. Only {product.stock_quantity} available.')
                    return redirect('inventory:stock_adjust')
            product.save()

            StockLog.objects.create(
                product=product,
                change_type=change_type,
                quantity=quantity,
                notes=notes,
            )
            messages.success(request, f'Stock updated for {product.name}!')
            return redirect('inventory:inventory_list')
    else:
        form = StockAdjustForm()
    return render(request, 'inventory/stock_adjust.html', {'form': form})


def stock_history(request):
    logs = StockLog.objects.select_related('product').all()
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    return render(request, 'inventory/stock_history.html', {'logs': logs})


def reports_view(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    low_stock = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lt=10).count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()
    total_value = Product.objects.aggregate(
        total=Sum(F('price') * F('stock_quantity'))
    )['total'] or 0
    total_stock_in = StockLog.objects.filter(change_type='IN').aggregate(
        total=Sum('quantity'))['total'] or 0
    total_stock_out = StockLog.objects.filter(change_type='OUT').aggregate(
        total=Sum('quantity'))['total'] or 0

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_value': total_value,
        'total_stock_in': total_stock_in,
        'total_stock_out': total_stock_out,
    }
    return render(request, 'inventory/reports.html', context)


def settings_view(request):
    return render(request, 'inventory/settings.html')
