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

from django.contrib import messages
from menu.models import MenuItem
from .models import Recipe
from django.db.models import Prefetch

@login_required
def manage_recipes(request):
    if not hasattr(request.user, 'hotelowner'):
        return redirect('owner_login')

    hotel = request.user.hotelowner.hotel

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_recipe':
            menu_item_id = request.POST.get('menu_item_id')
            inventory_item_id = request.POST.get('inventory_item_id')
            quantity = request.POST.get('quantity')
            
            menu_item = get_object_or_404(MenuItem, id=menu_item_id, hotel=hotel)
            inventory_item = get_object_or_404(InventoryItem, id=inventory_item_id, hotel=hotel)
            
            Recipe.objects.update_or_create(
                menu_item=menu_item,
                inventory_item=inventory_item,
                defaults={'quantity_required': Decimal(quantity)}
            )
            messages.success(request, f"Recipe configured for {menu_item.name}.")
            return redirect('manage_recipes')
            
        elif action == 'delete_recipe':
            recipe_id = request.POST.get('recipe_id')
            recipe = get_object_or_404(Recipe, id=recipe_id, menu_item__hotel=hotel)
            recipe.delete()
            messages.success(request, "Ingredient removed from recipe.")
            return redirect('manage_recipes')

    menu_items = MenuItem.objects.filter(hotel=hotel).prefetch_related(
        Prefetch('recipe_set', queryset=Recipe.objects.select_related('inventory_item'))
    )
    inventory_items = InventoryItem.objects.filter(hotel=hotel)

    return render(request, 'inventory/manage_recipes.html', {
        'menu_items': menu_items,
        'inventory_items': inventory_items
    })
