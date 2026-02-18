from django.db import models
from django.utils import timezone
from datetime import timedelta

from hotels.models import Hotel, Table
from menu.models import MenuItem


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('dine_in', 'Dine In'),
        ('parcel', 'Parcel'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='dine_in')
    order_id = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

   
    is_new = models.BooleanField(default=True)
    highlight_until = models.DateTimeField(null=True, blank=True)

    def mark_for_kitchen(self):
        self.is_new = True
        self.highlight_until = timezone.now() + timedelta(minutes=10)
        self.save(update_fields=['is_new', 'highlight_until'])

    def __str__(self):
        return self.order_id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def get_subtotal(self):
        return self.quantity * self.price
