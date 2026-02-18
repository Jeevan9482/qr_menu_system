from django.contrib import admin
from .models import Hotel, Table


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'table_number')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hotel=request.user.hotelowner.hotel)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.hotel = request.user.hotelowner.hotel
        super().save_model(request, obj, form, change)
