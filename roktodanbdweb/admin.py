from django.contrib import admin
from .models import Donor

# Register your models here.

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'blood_group', 'district', 'registration_date')
    list_filter = ('blood_group', 'district')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email')