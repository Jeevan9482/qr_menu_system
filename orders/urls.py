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
    path('bill/<str:order_id>/', views.bill_receipt, name='bill_receipt'),

    # Draft Bills
    path('draft/', views.draft_list, name='draft_list'),
    path('draft/<int:slot>/', views.draft_billing, name='draft_billing'),
    path('draft/<int:slot>/clear/', views.draft_clear, name='draft_clear'),

]
