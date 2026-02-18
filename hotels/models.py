from django.db import models
import qrcode
from django.conf import settings
from django.core.files import File
from io import BytesIO


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    logo = models.ImageField(upload_to='hotel_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='tables'
    )
    table_number = models.PositiveIntegerField()

    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('hotel', 'table_number')

    def __str__(self):
        return f"Table {self.table_number} - {self.hotel.name}"
