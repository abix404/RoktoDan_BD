from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm
from .models import Donor

def home(request):
    return render(request, 'home.html')
# Create your views here.

def about_us(request):
    return render(request, 'about_us.html')


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