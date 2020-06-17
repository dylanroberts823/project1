from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import RegistrationForm

from orders.models import Category, Item


# Create your views here.
#Taken directly from source code 7
def index(request):
    if not request.user.is_authenticated:
        return render(request, "users/login.html", {"message": None})
    return HttpResponseRedirect("orders/menu")

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "users/login.html", {"message": "Invalid credentials."})
    else:
        return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {"message": "Logged out."})

def register_view(request):
#Shoutout for the tutorial to https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})
