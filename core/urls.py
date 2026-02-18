from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from menu import views as menu_views

from django.shortcuts import redirect
from accounts.views import landing_page, owner_login



urlpatterns = [

    path('', include('hotels.urls')),
    path('', landing_page),
    path('owner-login/', owner_login),
    path('admin-login/', lambda r: redirect('/admin/')),
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('menu/<int:hotel_id>/<int:table_id>/',menu_views.customer_menu,name='customer_menu'),
    path('inventory/', include('inventory.urls')),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
