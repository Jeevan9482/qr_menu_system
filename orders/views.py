import uuid
from decimal import Decimal
from django.shortcuts import redirect, render
from .models import Order, OrderItem
from hotels.models import Hotel, Table
from menu.models import MenuItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from asgiref.sync import async_to_sync

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from menu.models import MenuItem, Category
from .models import Order, OrderItem
from inventory.services import deduct_inventory

import json


from django.http import JsonResponse, HttpResponse

def place_order(request, hotel_id, table_id):
    cart = request.session.get('cart')
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    hotel = Hotel.objects.get(id=hotel_id)
    table = Table.objects.get(id=table_id, hotel=hotel)

    total = Decimal('0.00')
    order = Order.objects.create(
        hotel=hotel,
        table=table,
        order_id=f"ORD{uuid.uuid4().hex[:6].upper()}",
        total_amount=0
    )

    for item_id, qty in cart.items():
        item = MenuItem.objects.get(id=item_id)
        OrderItem.objects.create(
            order=order,
            menu_item=item,
            quantity=qty,
            price=item.price
        )
        total += item.price * qty

    order.total_amount = total
    order.mark_for_kitchen()
    order.save()
    deduct_inventory(order)

    

    request.session['cart'] = {}

    return JsonResponse({
        'success': True,
        'order_id': order.order_id,
        'total': str(total)
    })



@login_required
def owner_orders(request):
    # super admin can see all
    if request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')
    else:
        hotel = request.user.hotelowner.hotel
        orders = Order.objects.filter(hotel=hotel).order_by('-created_at')

    context = {
        'orders': orders
    }
    return render(request, 'orders/owner_orders.html', context)

@login_required
def order_detail(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, order_id=order_id)
    else:
        order = get_object_or_404(
            Order,
            order_id=order_id,
            hotel=request.user.hotelowner.hotel
        )

    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def complete_order(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, order_id=order_id)
    else:
        order = get_object_or_404(
            Order,
            order_id=order_id,
            hotel=request.user.hotelowner.hotel
        )

    order.is_completed = True
    order.save()

    # 🔁 Redirect logic
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('owner_orders')



@login_required
def owner_dashboard(request):
    hotel = request.user.hotelowner.hotel

    live_orders = Order.objects.filter(
        hotel=hotel,
        is_completed=False
    ).order_by('-created_at')

    completed_orders = Order.objects.filter(
        hotel=hotel,
        is_completed=True
    ).order_by('-created_at')[:20]

    tables = Table.objects.filter(hotel=hotel)

    context = {
        'hotel': hotel,
        'live_orders': live_orders,
        'completed_orders': completed_orders,
        'tables': tables
    }
    return render(request, 'owner/dashboard.html', context)



@login_required
def completed_orders(request):
    hotel = request.user.hotelowner.hotel

    orders = (
        Order.objects
        .filter(hotel=hotel, is_completed=True)
        .prefetch_related('items__menu_item')
        .order_by('-created_at')
    )

    start = request.GET.get('start')
    end = request.GET.get('end')

    if start:
        orders = orders.filter(created_at__date__gte=start)
    if end:
        orders = orders.filter(created_at__date__lte=end)

    return render(
        request,
        'orders/history/completed_orders.html',
        {'orders': orders}
    )


def get_subtotal(self):
    return self.quantity * self.price


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
            hotel=hotel,                     # 🔴 VERY IMPORTANT
            category_id=request.POST['category'],
            name=request.POST['name'],
            price=request.POST['price'],
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

from django.utils import timezone

@login_required
def kitchen_display(request):
    hotel = request.user.hotelowner.hotel
    now = timezone.now()

    orders = (
        Order.objects
        .filter(hotel=hotel, is_completed=False)
        .exclude(draft_slot__isnull=False, is_sent_to_kds=False)
        .prefetch_related('items__menu_item')
        .order_by('-created_at')
    )

    return render(request, 'orders/kitchen_display.html', {
        'orders': orders,
        'now': now
    })

@login_required
def owner_billing(request):
    hotel = request.user.hotelowner.hotel
    
    if request.method == 'POST':
        action = request.POST.get('action', 'place_order')
        order_type = request.POST.get('order_type')
        item_ids = request.POST.getlist('items')
        quantities = request.POST.getlist('quantities')
        
        if not item_ids:
            return redirect('owner_billing')

        if action == 'save_draft':
            # Find an available draft slot (1-10)
            available_slot = None
            for slot in range(1, 11):
                if not Order.objects.filter(hotel=hotel, draft_slot=slot, is_completed=False).exists():
                    available_slot = slot
                    break
            
            if not available_slot:
                from django.contrib import messages
                messages.error(request, 'All 10 draft slots are currently full. Please complete or clear a draft first.')
                return redirect('owner_billing')

            order = Order(
                hotel=hotel,
                order_id=f"DFT{available_slot:02d}{uuid.uuid4().hex[:4].upper()}",
                order_type=order_type,
                total_amount=0,
                is_new=True,
                is_completed=False,
                draft_slot=available_slot
            )
        else:
            # Normal 'place_order' process
            order = Order(
                hotel=hotel,
                order_id=f"POS{uuid.uuid4().hex[:6].upper()}",
                order_type=order_type,
                total_amount=0,
                is_new=True,
                is_completed=True # Immediately flag complete for normal POS orders so they skip KDS/Drafts if desired, or let standard POS logic play out
            )
            # Actually standard POS is marked for KDS, so we defer to the original behavior of is_completed=False initially unless this system normally closes them later
            order.is_completed = False

        if order_type == 'dine_in':
            table_id = request.POST.get('table')
            if table_id:
                order.table = Table.objects.get(id=table_id, hotel=hotel)
        
        order.save()

        total = Decimal('0.00')
        
        # Process Items
        for i, item_id in enumerate(item_ids):
            qty = int(quantities[i])
            if qty > 0:
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=qty,
                    price=menu_item.price
                )
                total += menu_item.price * qty

        order.total_amount = total
        
        if action == 'save_draft':
            order.mark_for_kitchen() # If you want drafts to show in kitchen, or ommit it. The existing draft system marks them based on earlier logic.
            order.save()
            deduct_inventory(order)
            from django.contrib import messages
            messages.success(request, f'Order successfully saved to Draft Slot {available_slot}.')
            return redirect('draft_list')
            
        else:
            # Normal Place Order Path
            order.save()
            # Deduct Inventory
            deduct_inventory(order)
            return redirect('bill_receipt', order_id=order.order_id)

    # GET Request
    categories = Category.objects.filter(hotel=hotel, is_active=True).prefetch_related('menuitem_set')
    tables = Table.objects.filter(hotel=hotel)
    
    return render(request, 'owner/billing.html', {
        'categories': categories, 
        'tables': tables
    })


from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta

@login_required
def owner_reports(request):
    hotel = request.user.hotelowner.hotel
    today = timezone.now().date()
    
    # Base QuerySet
    orders = Order.objects.filter(hotel=hotel, is_completed=True)
    
    # 1. Dashboard Cards Data
    daily_sales = orders.filter(created_at__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    daily_orders = orders.filter(created_at__date=today).count()
    
    monthly_sales = orders.filter(created_at__month=today.month, created_at__year=today.year).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_orders = orders.filter(created_at__month=today.month, created_at__year=today.year).count()
    
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()

    # 2. Chart Data (Last 7 Days)
    last_7_days = today - timedelta(days=6)
    sales_data = (
        orders.filter(created_at__date__gte=last_7_days)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('date')
    )
    
    chart_labels = []
    chart_values = []
    chart_dates = []  # ISO dates for click navigation
    current_date = last_7_days
    
    sales_dict = {item['date']: item['total'] for item in sales_data}
    
    for i in range(7):
        chart_labels.append(current_date.strftime('%d %b'))
        chart_values.append(float(sales_dict.get(current_date, 0)))
        chart_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    # 3. Top Selling Items
    top_items_qs = (
        OrderItem.objects.filter(order__hotel=hotel, order__is_completed=True)
        .values('menu_item__name', 'price')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )
    
    top_items_list = []
    for item in top_items_qs:
        top_items_list.append({
            'name': item['menu_item__name'],
            'qty': item['total_qty'],
            'revenue': item['total_qty'] * item['price']
        })

    context = {
        'daily_sales': daily_sales,
        'daily_orders': daily_orders,
        'monthly_sales': monthly_sales,
        'monthly_orders': monthly_orders,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'chart_dates': json.dumps(chart_dates),
        'top_items': top_items_list,
    }
    
    return render(request, 'owner/reports.html', context)


def _get_report_orders(hotel, period):
    """Helper: returns (orders_qs, period_label, filename_part) for a given period string."""
    from django.utils import timezone as tz
    today = tz.now().date()
    orders = Order.objects.filter(hotel=hotel, is_completed=True).prefetch_related('items__menu_item').order_by('-created_at')

    if period == 'today':
        orders = orders.filter(created_at__date=today)
        label = f"Today's Orders — {today.strftime('%d %b %Y')}"
        fname = f"report_today_{today.strftime('%Y%m%d')}"
    elif period == 'monthly':
        orders = orders.filter(created_at__month=today.month, created_at__year=today.year)
        label = f"Monthly Orders — {today.strftime('%B %Y')}"
        fname = f"report_monthly_{today.strftime('%Y%m')}"
    elif period and len(period) == 10:  # YYYY-MM-DD
        try:
            from datetime import date as date_cls
            d = date_cls.fromisoformat(period)
            orders = orders.filter(created_at__date=d)
            label = f"Orders on {d.strftime('%d %b %Y')}"
            fname = f"report_{period}"
        except ValueError:
            orders = orders.none()
            label = "Orders"
            fname = "report"
    else:  # 'all' or anything else
        label = "All-Time Orders"
        fname = "report_all"

    return orders, label, fname


@login_required
def report_detail(request):
    hotel = request.user.hotelowner.hotel
    period = request.GET.get('period', 'all')
    orders, label, _ = _get_report_orders(hotel, period)

    total_revenue = sum(o.total_amount for o in orders)
    total_count = orders.count()

    context = {
        'orders': orders,
        'label': label,
        'period': period,
        'total_revenue': total_revenue,
        'total_count': total_count,
        'hotel': hotel,
    }
    return render(request, 'owner/report_detail.html', context)


@login_required
def report_detail_pdf(request):
    from io import BytesIO
    from xhtml2pdf import pisa
    from django.template.loader import render_to_string
    from django.utils import timezone as tz

    hotel = request.user.hotelowner.hotel
    period = request.GET.get('period', 'all')
    orders, label, fname = _get_report_orders(hotel, period)

    total_revenue = sum(o.total_amount for o in orders)
    total_count = orders.count()

    context = {
        'orders': orders,
        'label': label,
        'period': period,
        'total_revenue': total_revenue,
        'total_count': total_count,
        'hotel': hotel,
        'generated_at': tz.now(),
    }

    html_string = render_to_string('owner/report_pdf.html', context)
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer)

    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{fname}.pdf"'
    return response


@login_required
def bill_receipt(request, order_id):
    hotel = request.user.hotelowner.hotel
    order = get_object_or_404(
        Order.objects.prefetch_related('items__menu_item'),
        order_id=order_id,
        hotel=hotel
    )
    return render(request, 'owner/bill_receipt.html', {'order': order, 'hotel': hotel})


# ──────────────────────────────────────────────
# DRAFT BILLS
# ──────────────────────────────────────────────

DRAFT_SLOTS = list(range(1, 11))  # slots 1-10


@login_required
def draft_list(request):
    """Shows the 10 draft slots for the hotel."""
    hotel = request.user.hotelowner.hotel

    # Fetch any open draft orders for this hotel
    drafts = {
        d.draft_slot: d
        for d in Order.objects.filter(
            hotel=hotel,
            draft_slot__isnull=False,
            is_completed=False
        ).prefetch_related('items')
    }

    slots = []
    for n in DRAFT_SLOTS:
        order = drafts.get(n)
        slots.append({
            'slot': n,
            'order': order,
            'item_count': order.items.count() if order else 0,
        })

    return render(request, 'owner/draft_list.html', {'slots': slots})


@login_required
def draft_billing(request, slot):
    """Billing form for a specific draft slot (1-10)."""
    if slot not in DRAFT_SLOTS:
        return redirect('draft_list')

    hotel = request.user.hotelowner.hotel

    # Load existing open draft for this slot, if any
    draft_order = Order.objects.filter(
        hotel=hotel, draft_slot=slot, is_completed=False
    ).prefetch_related('items__menu_item').first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')  # 'save' | 'close'

        # ── CLOSE: finalise → receipt ──
        if action == 'close':
            if draft_order:
                draft_order.is_completed = True
                draft_order.draft_slot = None   # free the slot
                draft_order.save()
                return redirect('bill_receipt', order_id=draft_order.order_id)
            return redirect('draft_billing', slot=slot)

        # ── SAVE: create or update draft ──
        item_ids   = request.POST.getlist('items')
        quantities = request.POST.getlist('quantities')

        # Check if at least one item has qty > 0
        has_items = any(int(q) > 0 for q in quantities if q.isdigit())
        if not has_items:
            return redirect('draft_billing', slot=slot)

        if draft_order is None:
            # Create a new draft order for this slot
            order_type = request.POST.get('order_type', 'dine_in')
            draft_order = Order(
                hotel=hotel,
                order_id=f"DFT{slot:02d}{uuid.uuid4().hex[:4].upper()}",
                order_type=order_type,
                total_amount=Decimal('0.00'),
                is_new=True,
                is_completed=False,
                draft_slot=slot,
            )
            if order_type == 'dine_in':
                table_id = request.POST.get('table')
                if table_id:
                    draft_order.table = Table.objects.get(id=table_id, hotel=hotel)
            draft_order.save()

        total_added = Decimal('0.00')
        for i, item_id in enumerate(item_ids):
            qty = int(quantities[i]) if i < len(quantities) else 0
            if qty > 0:
                menu_item = MenuItem.objects.get(id=item_id, hotel=hotel)
                # Merge if item already exists
                existing = OrderItem.objects.filter(
                    order=draft_order, menu_item=menu_item
                ).first()
                if existing:
                    existing.quantity += qty
                    existing.save()
                    total_added += menu_item.price * qty
                else:
                    OrderItem.objects.create(
                        order=draft_order,
                        menu_item=menu_item,
                        quantity=qty,
                        price=menu_item.price,
                    )
                    total_added += menu_item.price * qty

        draft_order.total_amount += total_added
        
        if action == 'send_kds':
            draft_order.is_sent_to_kds = True
            draft_order.mark_for_kitchen()   # show and highlight in KDS
        elif draft_order.is_sent_to_kds:
            draft_order.mark_for_kitchen()   # re-highlight if already sent
            
        draft_order.save()

        deduct_inventory(draft_order)

        if action == 'send_kds':
            from django.contrib import messages
            messages.success(request, f'Draft #{slot} has been placed to the Kitchen Display System.')
            
        return redirect('draft_billing', slot=slot)

    # ── GET ──
    categories = Category.objects.filter(hotel=hotel, is_active=True).prefetch_related('menuitem_set')
    tables = Table.objects.filter(hotel=hotel)

    return render(request, 'owner/draft_billing.html', {
        'slot': slot,
        'draft_order': draft_order,
        'categories': categories,
        'tables': tables,
    })


@login_required
def draft_clear(request, slot):
    """Clears (deletes) the draft order for a slot."""
    if request.method == 'POST':
        hotel = request.user.hotelowner.hotel
        Order.objects.filter(
            hotel=hotel, draft_slot=slot, is_completed=False
        ).delete()
    return redirect('draft_list')
