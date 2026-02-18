from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import InventoryItem


@login_required
def inventory_dashboard(request):
    if not hasattr(request.user, 'hotelowner'):
        return redirect('owner_login')

    hotel = request.user.hotelowner.hotel
    items = InventoryItem.objects.filter(hotel=hotel)
    low_stock = items.filter(quantity__lte=models.F('minimum_quantity'))

    return render(request, 'inventory/dashboard.html', {
        'items': items,
        'low_stock': low_stock
    })


@login_required
def update_stock(request, item_id):
    if not hasattr(request.user, 'hotelowner'):
        return redirect('owner_login')

    hotel = request.user.hotelowner.hotel
    item = get_object_or_404(InventoryItem, id=item_id, hotel=hotel)

    if request.method == 'POST':
        added_qty = request.POST.get('quantity')
        item.quantity += Decimal(added_qty)
        item.save()

    return redirect('inventory_dashboard')
@login_required
def add_inventory_item(request):
    if not hasattr(request.user, 'hotelowner'):
        return redirect('owner_login')

    hotel = request.user.hotelowner.hotel

    if request.method == 'POST':
        InventoryItem.objects.create(
            hotel=hotel,
            name=request.POST['name'],
            quantity=Decimal(request.POST['quantity']),
            minimum_quantity=Decimal(request.POST['minimum_quantity']),
            unit=request.POST['unit']
        )
        return redirect('inventory_dashboard')

    return render(request, 'inventory/add_item.html')
