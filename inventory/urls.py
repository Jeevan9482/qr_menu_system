from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    path('update/<int:item_id>/', views.update_stock, name='update_stock'),
    path('add/', views.add_inventory_item, name='add_inventory_item'),
    path('recipes/', views.manage_recipes, name='manage_recipes'),
]
