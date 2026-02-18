from django.db import models
from django.contrib.auth.models import User
from hotels.models import Hotel

class HotelOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"
