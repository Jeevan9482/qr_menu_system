from django.db import models
from hotels.models import Hotel
from menu.models import MenuItem


class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('ltr', 'Liter'),
        ('pcs', 'Pieces'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.quantity <= self.minimum_quantity

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class Recipe(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.menu_item.hotel != self.inventory_item.hotel:
            raise ValueError("Hotel mismatch between MenuItem and InventoryItem")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item.name} → {self.inventory_item.name}"
