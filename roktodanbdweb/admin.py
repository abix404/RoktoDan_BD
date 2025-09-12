from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from .models import Donor, Recipient, DonationHistory, BloodRequest, DonorResponse
from .models import DonorPoints, PointTransaction, DonorBadge, WithdrawalRequest

class DonorInline(admin.StackedInline):
    """
    Inline admin for Donor model to show in User admin
    """
    model = Donor
    can_delete = False
    verbose_name = "Donor Profile"
    verbose_name_plural = "Donor Profiles"
    fields = (
        ('first_name', 'last_name'),
        ('phone_number', 'email'),
        ('age', 'weight', 'blood_group'),
        ('house_holding_no', 'road_block'),
        ('thana', 'post_office', 'district'),
        ('last_donation_month', 'last_donation_year'),
        'profile_image',
    )


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """
    Enhanced Donor admin with comprehensive management features
    """
    list_display = (
        'get_full_name',
        'blood_group',
        'age',
        'weight',
        'thana',
        'phone_number',
        'get_user_email',
        'get_availability_status',
        'get_last_donation',
        'get_date_joined',
        'get_profile_image'
    )

    list_filter = (
        'blood_group',
        'thana',
        'district',
        'age',
        'last_donation_month',
        'last_donation_year',
        'user__date_joined',
    )

    search_fields = (
        'first_name',
        'last_name',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
        'thana',
        'district',
        'house_holding_no'
    )

    readonly_fields = (
        'user',
        'get_date_joined',
        'get_user_info',
        'get_full_address',
        'get_donation_eligibility'
    )

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'get_user_info',
                ('first_name', 'last_name'),
                'age',
                'weight',
                'blood_group',
                'phone_number',
                'profile_image'
            )
        }),
        ('Address Information', {
            'fields': (
                'get_full_address',
                'house_holding_no',
                'road_block',
                ('thana', 'post_office'),
                'district'
            )
        }),
        ('Donation History', {
            'fields': (
                'get_donation_eligibility',
                ('last_donation_month', 'last_donation_year')
            )
        }),
        ('Account Information', {
            'fields': ('user', 'get_date_joined'),
            'classes': ('collapse',)
        })
    )

    actions = [
        'mark_as_available',
        'mark_as_unavailable',
        'send_donation_reminder',
        'export_donor_list'
    ]

    # Custom methods for display
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "No Name"

    get_full_name.short_description = "Full Name"
    get_full_name.admin_order_field = 'first_name'

    def get_user_email(self, obj):
        if hasattr(obj, 'email') and obj.email:
            return obj.email
        elif obj.user:
            return obj.user.email
        return "No Email"

    get_user_email.short_description = "Email"
    get_user_email.admin_order_field = 'user__email'

    def get_date_joined(self, obj):
        if obj.user:
            return obj.user.date_joined.strftime("%d %b %Y")
        return "No User"

    get_date_joined.short_description = "Registration Date"
    get_date_joined.admin_order_field = 'user__date_joined'

    def get_profile_image(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "No Image"

    get_profile_image.short_description = "Profile Picture"

    def get_availability_status(self, obj):
        # Calculate if donor is eligible to donate (3+ months since last donation)
        if not obj.last_donation_month or not obj.last_donation_year:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Available (Never donated)</span>'
            )

        try:
            last_donation_date = datetime(
                int(obj.last_donation_year),
                self.get_month_number(obj.last_donation_month),
                1
            )

            # Check if 3+ months have passed
            three_months_ago = timezone.now() - timedelta(days=90)

            if last_donation_date.replace(tzinfo=timezone.now().tzinfo) < three_months_ago:
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Available</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⏳ Not Available</span>'
                )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: gray;">❓ Unknown</span>'
            )

    get_availability_status.short_description = "Donation Status"

    def get_last_donation(self, obj):
        if obj.last_donation_month and obj.last_donation_year:
            return f"{obj.last_donation_month} {obj.last_donation_year}"
        return "Never donated"

    get_last_donation.short_description = "Last Donation"

    def get_user_info(self, obj):
        if obj.user:
            user_link = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html(
                '<a href="{}" target="_blank">{} ({})</a>',
                user_link,
                obj.user.username,
                obj.user.email
            )
        return "No User"

    get_user_info.short_description = "Associated User Account"

    def get_full_address(self, obj):
        address_parts = [
            obj.house_holding_no,
            obj.road_block,
            obj.thana,
            obj.post_office,
            obj.district
        ]
        return ", ".join([part for part in address_parts if part])

    get_full_address.short_description = "Full Address"

    def get_donation_eligibility(self, obj):
        if not obj.last_donation_month or not obj.last_donation_year:
            return format_html(
                '<div style="color: green; font-weight: bold;">✓ Eligible to donate (Never donated before)</div>'
            )

        try:
            last_donation_date = datetime(
                int(obj.last_donation_year),
                self.get_month_number(obj.last_donation_month),
                1
            )

            next_eligible_date = last_donation_date + timedelta(days=90)  # 3 months
            today = datetime.now()

            if today >= next_eligible_date:
                return format_html(
                    '<div style="color: green; font-weight: bold;">✓ Eligible to donate</div>'
                )
            else:
                days_remaining = (next_eligible_date - today).days
                return format_html(
                    '<div style="color: orange; font-weight: bold;">⏳ Can donate after {} days ({})</div>',
                    days_remaining,
                    next_eligible_date.strftime("%d %b %Y")
                )
        except (ValueError, TypeError):
            return format_html(
                '<div style="color: gray;">❓ Unable to calculate eligibility</div>'
            )

    get_donation_eligibility.short_description = "Donation Eligibility"

    @staticmethod
    def get_month_number(month_name):
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return months.get(month_name, 1)

    # Custom admin actions
    def mark_as_available(self, request, queryset):
        self.message_user(request, 'Availability feature will be implemented soon.')

    mark_as_available.short_description = "Mark selected donors as available"

    def mark_as_unavailable(self, request, queryset):
        self.message_user(request, 'Availability feature will be implemented soon.')

    mark_as_unavailable.short_description = "Mark selected donors as unavailable"

    def send_donation_reminder(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Donation reminders will be sent to {count} donors (feature coming soon).'
        )

    send_donation_reminder.short_description = "Send donation reminder"

    def export_donor_list(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Export feature for {count} donors coming soon.'
        )

    export_donor_list.short_description = "Export donor list"

    # Override get_queryset to add optimizations
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'blood_group', 'phone_number',
        'user_email', 'thana', 'district', 'created_at', 'is_active', 'has_user_account'
    ]
    list_filter = ['blood_group', 'thana', 'district', 'is_active', 'created_at', 'user']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'user__email',
                     'user__first_name', 'user__last_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Account', {
            'fields': ('user', 'has_user_account_display'),
            'description': 'Django User account linked to this recipient'
        }),
        ('Personal Information', {
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
        return super().get_queryset(request).select_related('user')

    actions = ['create_user_accounts_for_selected']

    def create_user_accounts_for_selected(self, request, queryset):
        """
        Admin action to create User accounts for recipients that don't have them
        """
        count = 0
        errors = []

        for recipient in queryset.filter(user__isnull=True):
            try:
                if User.objects.filter(email=recipient.email).exists():
                    errors.append(f"User with email {recipient.email} already exists")
                    continue

                user = User.objects.create_user(
                    username=recipient.email,
                    email=recipient.email,
                    first_name=recipient.first_name,
                    last_name=recipient.last_name,
                    password=make_password('TempPassword123!')
                )

                recipient.user = user
                recipient.save()
                count += 1

            except Exception as e:
                errors.append(f"Failed to create user for {recipient.full_name}: {str(e)}")

        if count:
            self.message_user(request, f"Successfully created {count} user accounts.")
        if errors:
            self.message_user(request, f"Errors: {'; '.join(errors)}", level='ERROR')

    create_user_accounts_for_selected.short_description = "Create User accounts for selected recipients"


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['get_donor_name', 'donation_date', 'recipient_name', 'blood_group', 'status', 'location', 'amount']
    list_filter = ['status', 'blood_group', 'donation_date', 'location']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'recipient_name', 'hospital_name', 'location']
    date_hierarchy = 'donation_date'
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    ordering = ['-donation_date']

    fieldsets = (
        ('Donation Information', {
            'fields': ('donor', 'donation_date', 'blood_group', 'amount', 'status')
        }),
        ('Recipient Information', {
            'fields': ('recipient_name', 'hospital_name', 'location', 'contact_number')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_donor_name(self, obj):
        if obj.donor and obj.donor.user:
            return f"{obj.donor.user.first_name} {obj.donor.user.last_name}"
        elif obj.donor:
            return f"{obj.donor.first_name} {obj.donor.last_name}" if hasattr(obj.donor,
                                                                              'first_name') else "Unknown Donor"
        return "No Donor"

    get_donor_name.short_description = "Donor Name"
    get_donor_name.admin_order_field = 'donor__user__first_name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('donor__user')

    actions = ['mark_as_completed', 'mark_as_pending', 'export_donation_history']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} donation records marked as completed.')

    mark_as_completed.short_description = "Mark selected donations as completed"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} donation records marked as pending.')

    mark_as_pending.short_description = "Mark selected donations as pending"

    def export_donation_history(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'Export feature for {count} donation records coming soon.')

    export_donation_history.short_description = "Export donation history"


class RecipientInline(admin.StackedInline):
    model = Recipient
    can_delete = False
    verbose_name_plural = 'Recipient Profile'
    fields = ('blood_group', 'phone_number', 'house_holding_no', 'road_block', 'thana', 'is_active')


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User admin that includes Donor and Recipient profiles
    """
    inlines = (DonorInline, RecipientInline)

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        # Only show donor inline if user has a donor profile
        if obj and hasattr(obj, 'donor'):
            inline_instances.append(DonorInline(self.model, self.admin_site))

        # Only show recipient inline if user has a recipient profile
        if obj and hasattr(obj, 'recipient'):
            inline_instances.append(RecipientInline(self.model, self.admin_site))

        return inline_instances

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group_needed', 'hospital_name', 'urgency_level', 'status', 'created_at']
    list_filter = ['blood_group_needed', 'urgency_level', 'status', 'thana', 'created_at']
    search_fields = ['patient_name', 'hospital_name', 'contact_person']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_request', 'response', 'response_date']
    list_filter = ['response', 'response_date']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'blood_request__patient_name']
    ordering = ['-response_date']


@admin.register(DonorPoints)
class DonorPointsAdmin(admin.ModelAdmin):
    list_display = [
        'get_donor_name',
        'total_points',
        'available_points',
        'withdrawn_points',
        'last_updated'
    ]
    list_filter = ['last_updated']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'donor__phone_number']
    readonly_fields = ['last_updated', 'get_donor_info', 'get_transaction_summary']

    fieldsets = (
        ('Donor Information', {
            'fields': ('donor', 'get_donor_info')
        }),
        ('Points Summary', {
            'fields': (
                'total_points',
                'available_points',
                'withdrawn_points',
                'get_transaction_summary'
            )
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )

    def get_donor_name(self, obj):
        return obj.donor.full_name

    get_donor_name.short_description = "Donor Name"
    get_donor_name.admin_order_field = 'donor__user__first_name'

    def get_donor_info(self, obj):
        donor_link = reverse('admin:myapp_donor_change', args=[obj.donor.pk])
        return format_html(
            '<a href="{}" target="_blank">{} ({})</a>',
            donor_link,
            obj.donor.full_name,
            obj.donor.blood_group
        )

    get_donor_info.short_description = "Donor Details"

    def get_transaction_summary(self, obj):
        earned_count = obj.transactions.filter(transaction_type='earned').count()
        withdrawn_count = obj.transactions.filter(transaction_type='withdrawn').count()
        return format_html(
            '<div>Earned Transactions: <strong>{}</strong></div>'
            '<div>Withdrawn Transactions: <strong>{}</strong></div>',
            earned_count, withdrawn_count
        )

    get_transaction_summary.short_description = "Transaction Summary"

    actions = ['award_bonus_points', 'reset_points']

    def award_bonus_points(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'Bonus points feature for {count} donors coming soon.')

    award_bonus_points.short_description = "Award bonus points"

    def reset_points(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'Point reset feature for {count} donors coming soon.')

    reset_points.short_description = "Reset points (Admin only)"


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'get_donor_name',
        'transaction_type',
        'points',
        'description',
        'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    search_fields = [
        'donor_points__donor__user__first_name',
        'donor_points__donor__user__last_name',
        'description'
    ]
    readonly_fields = ['created_at']

    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'donor_points',
                'transaction_type',
                'points',
                'description'
            )
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_donor_name(self, obj):
        return obj.donor_points.donor.full_name

    get_donor_name.short_description = "Donor"
    get_donor_name.admin_order_field = 'donor_points__donor__user__first_name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'donor_points__donor__user'
        )


@admin.register(DonorBadge)
class DonorBadgeAdmin(admin.ModelAdmin):
    list_display = [
        'get_donor_name',
        'get_badge_display',
        'donation_count_when_earned',
        'earned_date'
    ]
    list_filter = ['badge_type', 'earned_date']
    search_fields = [
        'donor__user__first_name',
        'donor__user__last_name',
        'donor__phone_number'
    ]
    readonly_fields = ['earned_date', 'get_badge_icon']

    fieldsets = (
        ('Badge Information', {
            'fields': (
                'donor',
                'badge_type',
                'get_badge_icon',
                'donation_count_when_earned'
            )
        }),
        ('Timestamp', {
            'fields': ('earned_date',),
            'classes': ('collapse',)
        }),
    )

    def get_donor_name(self, obj):
        return obj.donor.full_name

    get_donor_name.short_description = "Donor Name"
    get_donor_name.admin_order_field = 'donor__user__first_name'

    def get_badge_display(self, obj):
        return format_html(
            '<span class="badge badge-{}" style="background: #{}; color: white; padding: 5px 10px; border-radius: 15px;">'
            '<i class="fas {}"></i> {}</span>',
            obj.badge_type,
            self.get_badge_color_hex(obj.badge_type),
            obj.badge_icon,
            obj.get_badge_type_display()
        )

    get_badge_display.short_description = "Badge"

    def get_badge_icon(self, obj):
        return format_html(
            '<i class="fas {} fa-2x" style="color: {};"></i>',
            obj.badge_icon,
            self.get_badge_color_hex(obj.badge_type)
        )

    get_badge_icon.short_description = "Badge Icon"

    def get_badge_color_hex(self, badge_type):
        colors = {
            'first_donor': '28a745',  # Green for first donation
            'regular_donor': '17a2b8',  # Blue for regular donor
            'milestone_donor': 'ffc107',  # Yellow for milestone
            'super_donor': 'dc3545',  # Red for super donor
            'legendary_donor': '6f42c1'  # Purple for legendary donor
        }
        return colors.get(badge_type, '6c757d')  # Default to grey if badge_type not found



@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = [
        'get_donor_name',
        'points_requested',
        'status',
        'requested_at',
        'processed_at'
    ]
    list_filter = ['status', 'requested_at']
    search_fields = [
        'donor_points__donor__user__first_name',
        'donor_points__donor__user__last_name',
        'donor_points__donor__phone_number'
    ]
    readonly_fields = ['requested_at', 'processed_at']

    fieldsets = (
        ('Withdrawal Details', {
            'fields': (
                'donor_points',
                'points_requested',
                'status',
            )
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )

    def get_donor_name(self, obj):
        return obj.donor_points.donor.full_name
    get_donor_name.short_description = "Donor"
    get_donor_name.admin_order_field = 'donor_points__donor__user__first_name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'donor_points__donor__user'
        )

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site headers
admin.site.site_header = "RoktoDan BD Administration"
admin.site.site_title = "RoktoDan BD Admin"
admin.site.index_title = "Welcome to RoktoDan BD Administration Panel"