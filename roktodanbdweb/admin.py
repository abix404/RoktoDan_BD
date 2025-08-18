from django.contrib import admin
from .models import Donor
from .models import Recipient

# Register your models here.

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'blood_group', 'district', 'registration_date')
    list_filter = ('blood_group', 'district')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email')

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'blood_group', 'phone_number',
        'email', 'thana', 'district', 'created_at', 'is_active'
    ]
    list_filter = ['blood_group', 'thana', 'district', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'age', 'phone_number', 'email', 'image')
        }),
        ('Blood Information', {
            'fields': ('blood_group',)
        }),
        ('Address Information', {
            'fields': ('house_holding_no', 'road_block', 'thana', 'post_office', 'district')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = 'Name'