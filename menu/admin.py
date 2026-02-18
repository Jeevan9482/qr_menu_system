from django.contrib import admin
from .models import Category, MenuItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hotel=request.user.hotelowner.hotel)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.hotel = request.user.hotelowner.hotel
        super().save_model(request, obj, form, change)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price', 'is_available')
    list_filter = ('is_available',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hotel=request.user.hotelowner.hotel)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.hotel = request.user.hotelowner.hotel
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category" and not request.user.is_superuser:
            kwargs["queryset"] = Category.objects.filter(
                hotel=request.user.hotelowner.hotel
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
