"""
URL configuration for roktodanbd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from roktodanbdweb import views as views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('oauth/', include('social_django.urls', namespace='social')),

    path('about_us/', views.about_us, name='about_us'),

    path('register_donor/', views.register_donor, name='register_donor'),

    path('sucess/', views.registration_success, name='success'),

    path('login/', views.user_login, name='login'),

    path('quick_register_recipient/', views.quick_register_recipient, name='quick_register_recipient'),

    path('donor_credit/', views.donor_credit, name='donor_credit'),

    path('donation_history/', views.donation_history, name='donation_history'),

    path('logout/', views.logout, name='logout'),
]
