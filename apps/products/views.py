from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product
from .forms import ProductForm
from apps.categories.models import Category


def product_list(request):
    products = Product.objects.select_related('category', 'supplier').all()

    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(brand__icontains=query)
        )

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)

    # Filter by stock status
    stock_status = request.GET.get('stock', '')
    if stock_status == 'low':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    elif stock_status == 'out':
        products = products.filter(stock_quantity=0)
    elif stock_status == 'in':
        products = products.filter(stock_quantity__gte=10)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status,
    }
    return render(request, 'products/product_list.html', context)


def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('products:product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_add.html', {'form': form})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_edit.html', {'form': form, 'product': product})


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'supplier'), pk=pk)
    stock_logs = product.stock_logs.all()[:20]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'stock_logs': stock_logs,
    })


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:product_list')
    return render(request, 'products/product_delete.html', {'product': product})
