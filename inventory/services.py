from decimal import Decimal
from .models import Recipe


def deduct_inventory(order):
    for order_item in order.items.all():
        recipes = Recipe.objects.filter(
            menu_item=order_item.menu_item,
            inventory_item__hotel=order.hotel
        )

        for recipe in recipes:
            required_qty = recipe.quantity_required * Decimal(order_item.quantity)
            inventory = recipe.inventory_item
            inventory.quantity -= required_qty
            inventory.save()
