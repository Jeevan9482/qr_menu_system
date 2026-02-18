from django.urls import path
from . import views

urlpatterns = [
    path('owner/tables/', views.owner_tables, name='owner_tables'),
    path('owner/tables/add/', views.add_table, name='add_table'),
    path('owner/tables/delete/<int:table_id>/', views.delete_table, name='delete_table'),
]
