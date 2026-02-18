from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/<int:hotel_id>/<int:table_id>/', views.view_cart, name='view_cart'),
    path('cart-summary/', views.cart_summary, name='cart_summary'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),

    path('owner/categories/', views.owner_categories, name='owner_categories'),
    path('owner/categories/add/', views.add_category, name='add_category'),
    path('owner/categories/delete/<int:cat_id>/', views.delete_category, name='delete_category'),


    path('owner/items/', views.owner_items, name='owner_items'),
    path('owner/items/add/', views.add_item, name='add_item'),
    path('owner/items/toggle/<int:item_id>/', views.toggle_item, name='toggle_item'),
    path('owner/items/delete/<int:item_id>/', views.delete_item, name='delete_item'),




]
