from django.shortcuts import redirect, render, get_object_or_404
from hotels.models import Hotel, Table
from .models import Category
from django.http import JsonResponse
from decimal import Decimal
from menu.models import MenuItem
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuItem, Category



def customer_menu(request, hotel_id, table_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)
    table = get_object_or_404(Table, id=table_id, hotel=hotel)

    categories = Category.objects.filter(
        hotel=hotel,
        is_active=True
    ).prefetch_related('menuitem_set')

    context = {
        'hotel': hotel,
        'table': table,
        'categories': categories,
    }
    return render(request, 'menu/customer_menu.html', context)


@require_POST
def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})

    item_id = str(item_id)
    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'cart_count': sum(cart.values())
    })


def view_cart(request, hotel_id, table_id):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for item_id, qty in cart.items():
        item = MenuItem.objects.get(id=item_id)
        subtotal = item.price * qty
        total += subtotal

        items.append({
            'item': item,
            'quantity': qty,
            'subtotal': subtotal
        })

    context = {
        'items': items,
        'total': total,
        'hotel_id': hotel_id,
        'table_id': table_id
    }
    return render(request, 'menu/cart.html', context)



def cart_summary(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for item_id, qty in cart.items():
        item = MenuItem.objects.get(id=item_id)
        subtotal = item.price * qty
        total += subtotal

        items.append({
            'id': item.id,
            'name': item.name,
            'price': str(item.price),
            'quantity': qty,
            'subtotal': str(subtotal)
        })

    return JsonResponse({
        'items': items,
        'total': str(total)
    })


@require_POST
def update_cart(request, item_id, action):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if action == 'add':
        cart[item_id] = cart.get(item_id, 0) + 1

    elif action == 'remove':
        if item_id in cart:
            cart[item_id] -= 1
            if cart[item_id] <= 0:
                del cart[item_id]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True})

@login_required
def owner_categories(request):
    hotel = request.user.hotelowner.hotel
    categories = Category.objects.filter(hotel=hotel)
    return render(request, 'owner/categories.html', {'categories': categories})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def add_category(request):
    hotel = request.user.hotelowner.hotel

    if request.method == 'POST':
        Category.objects.create(
            hotel=hotel,                 # ✅ THIS WAS MISSING
            name=request.POST['name']
        )

    return redirect('owner_categories')


@login_required
def delete_category(request, cat_id):
    hotel = request.user.hotelowner.hotel
    category = get_object_or_404(Category, id=cat_id, hotel=hotel)
    category.delete()
    return redirect('owner_categories')

@login_required
def owner_items(request):
    hotel = request.user.hotelowner.hotel
    items = MenuItem.objects.filter(hotel=hotel)
    categories = Category.objects.filter(hotel=hotel)

    return render(request, 'owner/items.html', {
        'items': items,
        'categories': categories
    })


@login_required
def add_item(request):
    hotel = request.user.hotelowner.hotel

    if request.method == 'POST':
        MenuItem.objects.create(
            hotel=hotel,
            category_id=request.POST['category'],
            name=request.POST['name'],
            price=request.POST['price'],
            food_type=request.POST.get('food_type', 'veg'),
            image=request.FILES.get('image'), 
            description=request.POST.get('description', ''), 
            is_available=True
        )


    return redirect('owner_items')

@login_required
def toggle_item(request, item_id):
    hotel = request.user.hotelowner.hotel
    item = get_object_or_404(MenuItem, id=item_id, hotel=hotel)

    item.is_available = not item.is_available
    item.save()

    return redirect('owner_items')

@login_required
def delete_item(request, item_id):
    hotel = request.user.hotelowner.hotel
    item = get_object_or_404(MenuItem, id=item_id, hotel=hotel)
    item.delete()
    return redirect('owner_items')
