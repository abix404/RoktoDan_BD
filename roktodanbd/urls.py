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

app_name = 'registration'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('oauth/', include('social_django.urls', namespace='social')),

    path('about_us/', views.about_us, name='about_us'),

    path('register_donor/', views.register_donor, name='register_donor'),

    path('sucess/', views.registration_success, name='success'),

    path('login/', views.user_login, name='login'),

    path('find_blood/', views.find_blood, name='find_blood'),

    path('donor_history/', views.donor_history, name='donor_history'),

    path('logout/', views.logout, name='logout'),

    path('register_recipient/', views.register_recipient, name='register_recipient'),

    path('success/', views.recipient_success, name='recipient_success'),

    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),

    path('profile/update/', views.donor_profile_update, name='donor_profile_update'),

    path('blood-requests/', views.blood_request_list, name='blood_request_list'),

    path('emergency-requests/', views.emergency_requests, name='emergency_requests'),

    #not setup yet
    path('matching/', views.matching, name='matching'),

    path('rewards/', views.rewards, name='rewards'),

    path('track-requests/', views.track_requests, name='track_requests'),
]
