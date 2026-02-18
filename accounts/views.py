from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def landing_page(request):
    return render(request, 'landing.html')


def owner_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user and not user.is_superuser:
            login(request, user)
            return redirect('/orders/dashboard/')
        else:
            messages.error(request, 'Invalid owner credentials')

    return render(request, 'accounts/owner_login.html')
