from django.db import models
from .models import InventoryItem

def inventory_context(request):
    """
    Injects global inventory data into all templates.
    Checks if the user is a hotel owner and provides the count of low-stock items.
    """
    context = {
        'global_low_stock_count': 0,
        'global_low_stock_items': []
    }
    
    if request.user.is_authenticated and hasattr(request.user, 'hotelowner'):
        hotel = request.user.hotelowner.hotel
        low_stock = InventoryItem.objects.filter(
            hotel=hotel,
            quantity__lte=models.F('minimum_quantity')
        )
        context['global_low_stock_count'] = low_stock.count()
        context['global_low_stock_items'] = list(low_stock)
        
    return context
