"""
URL configuration for roktodanbd project.

The `urlpatterns` list routes URLs to views.
For more information see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from roktodanbdweb import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home & Info
    path('', views.home, name='home'),
    path('about_us/', views.about_us, name='about_us'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),

    # Donor Registration & Dashboard
    path('register_donor/', views.register_donor, name='register_donor'),
    path('sucess/', views.registration_success, name='success'),   # (typo: maybe should be "success")
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('profile/update/', views.donor_profile_update, name='donor_profile_update'),
    path('donor_history/', views.donor_history, name='donor_history'),

    # Recipient Registration
    path('register_recipient/', views.register_recipient, name='register_recipient'),
    path('success/', views.recipient_success, name='recipient_success'),

    # Blood Requests
    path('find_blood/', views.find_blood, name='find_blood'),
    path('blood-requests/', views.blood_request_list, name='blood_request_list'),
    path('emergency-requests/', views.emergency_requests, name='emergency_requests'),
    path('track-requests/', views.track_requests, name='track_requests'),
    path('respond-to-request/<int:request_id>/', views.respond_to_request, name='respond_to_request'),

    # Rewards & Matching
    path('rewards/', views.rewards, name='rewards'),
    path('matching/', views.matching, name='matching'),
]

# Serve media files (profile images, uploads) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
