from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})


def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('suppliers:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_add.html', {'form': form})


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('suppliers:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_edit.html', {'form': form, 'supplier': supplier})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('suppliers:supplier_list')
    return render(request, 'suppliers/supplier_delete.html', {'supplier': supplier})
