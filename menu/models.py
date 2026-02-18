from django.db import models
from hotels.models import Hotel

class Category(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('hotel', 'name')

    def __str__(self):
        return f"{self.name} ({self.hotel.name})"

class MenuItem(models.Model):
    VEG = 'veg'
    NON_VEG = 'nonveg'

    FOOD_TYPE_CHOICES = [
        (VEG, 'Veg'),
        (NON_VEG, 'Non-Veg'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    food_type = models.CharField(
        max_length=10,
        choices=FOOD_TYPE_CHOICES,
        default=VEG
    )

    def __str__(self):
        return f"{self.name} ({self.food_type}) - {self.hotel.name}"

