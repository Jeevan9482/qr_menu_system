from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Table
import qrcode
from io import BytesIO
from django.core.files import File

from io import BytesIO
from django.core.files import File
import qrcode

@login_required
def owner_tables(request):
    hotel = request.user.hotelowner.hotel
    tables = Table.objects.filter(hotel=hotel)

    for table in tables:
        if not table.qr_code:
            qr_url = f"http://192.168.1.5:8000/menu/{hotel.id}/{table.id}/"
            qr = qrcode.make(qr_url)
            buffer = BytesIO()
            qr.save(buffer)
            table.qr_code.save(f"table_{table.id}.png", File(buffer))
            table.save()

    return render(request, 'owner/tables.html', {'tables': tables})


@login_required
def add_table(request):
    hotel = request.user.hotelowner.hotel

    if request.method == 'POST':
        number = request.POST['table_number']

        if Table.objects.filter(hotel=hotel, table_number=number).exists():
            return redirect('owner_tables')

        table = Table.objects.create(
            hotel=hotel,
            table_number=number
        )

        qr_url = f"http://10.79.30.134:8000/menu/{hotel.id}/{table.id}/"

        qr = qrcode.make(qr_url)
        buffer = BytesIO()
        qr.save(buffer)
        table.qr_code.save(f"table_{table.id}.png", File(buffer))
        table.save()

    return redirect('owner_tables')



@login_required
def delete_table(request, table_id):
    hotel = request.user.hotelowner.hotel
    table = get_object_or_404(Table, id=table_id, hotel=hotel)
    table.delete()
    return redirect('owner_tables')
