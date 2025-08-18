from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Donor


def home(request):
    return render(request, 'home.html')
# Create your views here.

def about_us(request):
    return render(request, 'about_us.html')

def donor_credit(request):
    return render(request, 'donor_credit.html')

def logout(request):
    return render(request, 'logout.html')

def donation_history(request):
    return render(request, 'donation_history.html')


def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('registration_success')
    else:
        form = DonorRegistrationForm()

    return render(request, 'register_donor.html', {'form': form})


def registration_success(request):
    return render(request, 'success.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Correctly passing both request and user
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')

    return render(request, 'login.html')

def quick_register_recipient(request):
    return render(request, 'quick_register_recipient.html')

