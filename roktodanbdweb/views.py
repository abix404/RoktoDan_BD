from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
# Create your views here.

def about_us(request):
    return render(request, 'about_us.html')

def as_donor(request):
    return render(request, 'registration/as_donor.html')