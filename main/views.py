from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from custom.models import *
from courses.models import *


# Create your views here.
@login_required
def index(request):
    return render(request,'main/index.html')

def loginPage(request):
    cores = Core.objects.filter(is_active=True).first()

    if request.user.is_authenticated:
        return redirect('dashboard2')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            AuditLogin.objects.create(user=user)
            return redirect('dashboard2')
        else:
            messages.error(request, 'Username ou Password la loos! Favor Prense fali!')

    context = {
        "title": "Pajina Login",
        "cores": cores,
    }
    return render(request, 'auth/login.html', context)
