from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Donor, Recipient


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
        'user_email', 'thana', 'district', 'created_at', 'is_active', 'has_user_account'
    ]
    list_filter = ['blood_group', 'thana', 'district', 'is_active', 'created_at', 'user']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'user__email', 'user__first_name',
                     'user__last_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Account', {
            'fields': ('user', 'has_user_account_display'),
            'description': 'Django User account linked to this recipient'
        }),
        ('Personal Information (Legacy)', {
            'fields': ('first_name', 'last_name', 'email', 'age', 'phone_number', 'image'),
            'description': 'These fields are used for recipients without linked User accounts'
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

    def user_email(self, obj):
        return obj.user_email

    user_email.short_description = 'Email'

    def has_user_account(self, obj):
        return obj.user is not None

    has_user_account.boolean = True
    has_user_account.short_description = 'Has User Account'

    def has_user_account_display(self, obj):
        if obj.user:
            return f"✅ Linked to User: {obj.user.username} ({obj.user.email})"
        else:
            return "❌ No linked User account (Legacy recipient)"

    has_user_account_display.short_description = 'User Account Status'

    def get_queryset(self, request):
        # Optimize queries by selecting related user data
        return super().get_queryset(request).select_related('user')

    actions = ['create_user_accounts_for_selected']

    def create_user_accounts_for_selected(self, request, queryset):
        """
        Admin action to create User accounts for recipients that don't have them
        """
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password

        count = 0
        errors = []

        for recipient in queryset.filter(user__isnull=True):
            try:
                # Check if user with this email already exists
                if User.objects.filter(email=recipient.email).exists():
                    errors.append(f"User with email {recipient.email} already exists")
                    continue

                # Create user account
                user = User.objects.create_user(
                    username=recipient.email,
                    email=recipient.email,
                    first_name=recipient.first_name,
                    last_name=recipient.last_name,
                    password=make_password('TempPassword123!')  # Temporary password
                )

                # Link recipient to user
                recipient.user = user
                recipient.save()
                count += 1

            except Exception as e:
                errors.append(f"Failed to create user for {recipient.full_name}: {str(e)}")

        # Show results
        if count:
            self.message_user(request, f"Successfully created {count} user accounts.")
        if errors:
            self.message_user(request, f"Errors: {'; '.join(errors)}", level='ERROR')

    create_user_accounts_for_selected.short_description = "Create User accounts for selected recipients"


# Optional: Create an inline admin to show recipient info in User admin
class RecipientInline(admin.StackedInline):
    model = Recipient
    can_delete = False
    verbose_name_plural = 'Recipient Profile'
    fields = ('blood_group', 'phone_number', 'house_holding_no', 'road_block', 'thana', 'is_active')


# Optional: Extend User admin to show recipient info
class UserAdmin(BaseUserAdmin):
    inlines = (RecipientInline,)

    def get_inline_instances(self, request, obj=None):
        # Only show recipient inline if user has a recipient profile
        if obj and hasattr(obj, 'recipient_profile'):
            return super().get_inline_instances(request, obj)
        return []


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)