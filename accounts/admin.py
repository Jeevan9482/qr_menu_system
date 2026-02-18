from django.contrib import admin
from .models import HotelOwner

@admin.register(HotelOwner)
class HotelOwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel')
