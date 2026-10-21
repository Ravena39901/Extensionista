from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category
from .forms import CategoryForm


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})


def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('categories:category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/category_add.html', {'form': form})


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/category_edit.html', {'form': form, 'category': category})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('categories:category_list')
    return render(request, 'categories/category_delete.html', {'category': category})
