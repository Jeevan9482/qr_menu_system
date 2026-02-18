from django.urls import path
from .views import place_order
from django.urls import path
from . import views

urlpatterns = [

    path('place/<int:hotel_id>/<int:table_id>/', place_order, name='place_order'),
    path('dashboard/', views.owner_orders, name='owner_orders'),
    path('billing/', views.owner_billing, name='owner_billing'),
    path('reports/', views.owner_reports, name='owner_reports'),
    path('reports/detail/', views.report_detail, name='report_detail'),
    path('reports/detail/pdf/', views.report_detail_pdf, name='report_detail_pdf'),
    path('detail/<str:order_id>/', views.order_detail, name='order_detail'),
    path('complete/<str:order_id>/', views.complete_order, name='complete_order'),
    path('history/', views.completed_orders, name='completed_orders'),
    path('kitchen/', views.kitchen_display, name='kitchen_display'),
    
]
