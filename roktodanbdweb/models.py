from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.utils import timezone


class Donor(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]

    THANA_CHOICES = [
        ('Adabar', 'Adabar'),
        ('Badda', 'Badda'),
        ('Banani', 'Banani'),
        ('Baridhara', 'Baridhara'),
        ('Dhanmondi', 'Dhanmondi'),
        ('Gulshan', 'Gulshan'),
        ('Hatirjheel', 'Hatirjheel'),
        ('Kafrul', 'Kafrul'),
        ('Kalabagan', 'Kalabagan'),
        ('Khilgaon', 'Khilgaon'),
        ('Khilkhet', 'Khilkhet'),
        ('Mirpur', 'Mirpur'),
        ('Mohammadpur', 'Mohammadpur'),
        ('Motijheel', 'Motijheel'),
        ('New Market', 'New Market'),
        ('Old Dhaka', 'Old Dhaka'),
        ('Pallabi', 'Pallabi'),
        ('Ramna', 'Ramna'),
        ('Rampura', 'Rampura'),
        ('Sabujbagh', 'Sabujbagh'),
        ('Shah Ali', 'Shah Ali'),
        ('Sher-e-Bangla Nagar', 'Sher-e-Bangla Nagar'),
        ('Tejgaon', 'Tejgaon'),
        ('Uttara', 'Uttara'),
        ('Wari', 'Wari'),
    ]

    POST_OFFICE_CHOICES = [
        ('Dhaka GPO', 'Dhaka GPO'),
        ('Banani', 'Banani'),
        ('Dhanmondi', 'Dhanmondi'),
        ('Gulshan', 'Gulshan'),
        ('Mirpur', 'Mirpur'),
        ('Mohammadpur', 'Mohammadpur'),
        ('Motijheel', 'Motijheel'),
        ('New Market', 'New Market'),
        ('Old Dhaka', 'Old Dhaka'),
        ('Ramna', 'Ramna'),
        ('Tejgaon', 'Tejgaon'),
        ('Uttara', 'Uttara'),
        ('Wari', 'Wari'),
    ]

    # Link to Django User model
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor',
        null=True,
        blank=True,
        help_text="Associated user account"
    )

    # Personal Information (from HTML form)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[MinLengthValidator(10)],
        help_text="Must be unique and at least 10 digits"
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(65)],
        help_text="Age must be between 18 and 65 years"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(50.0)],
        default=60.0,
        help_text="Weight in kg (minimum 50kg required for donation)"
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        help_text="Donor's blood group"
    )

    # Address Information (matching HTML form structure)
    house_holding_no = models.CharField(
        max_length=50,
        default='N/A',
        help_text="House holding number"
    )
    road_block = models.CharField(
        max_length=100,
        default='N/A',
        help_text="Road or block name/number"
    )
    thana = models.CharField(
        max_length=50,
        choices=THANA_CHOICES,
        default='Dhaka',
        help_text="Thana/Police station"
    )
    post_office = models.CharField(
        max_length=50,
        choices=POST_OFFICE_CHOICES,
        default='Dhaka GPO',
        help_text="Nearest post office"
    )
    district = models.CharField(
        max_length=50,
        default='Dhaka',
        help_text="District name"
    )

    # Donation History
    last_donation_month = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES,
        blank=True,
        null=True,
        help_text="Month of last blood donation (optional)"
    )
    last_donation_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text="Year of last blood donation (optional)"
    )

    # Profile Image
    profile_image = models.ImageField(
        upload_to='donor_images/',
        blank=True,
        null=True,
        help_text="Profile picture (max 5MB)"
    )

    # Health Declarations (from HTML form)
    health_declaration = models.BooleanField(
        default=False,
        help_text="Declared good health in past 3 months"
    )
    medication_declaration = models.BooleanField(
        default=False,
        help_text="Not taking medications affecting donation"
    )
    consent_declaration = models.BooleanField(
        default=False,
        help_text="Consent to donate blood"
    )

    # System Fields
    registration_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of registration"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the donor profile is active"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the donor is currently available for donation"
    )

    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['thana']),
            models.Index(fields=['district']),
            models.Index(fields=['is_active', 'is_available']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.blood_group}) - {self.thana}"

    @property
    def full_name(self):
        """Get donor's full name from associated User model"""
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def email(self):
        """Get donor's email from associated User model"""
        return self.user.email

    @property
    def first_name(self):
        """Get donor's first name from associated User model"""
        return self.user.first_name

    @property
    def last_name(self):
        """Get donor's last name from associated User model"""
        return self.user.last_name

    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [
            self.house_holding_no,
            self.road_block,
            self.thana,
            self.post_office,
            self.district
        ]
        return ", ".join([part for part in address_parts if part])

    @property
    def can_donate(self):
        """
        Check if donor is eligible to donate based on last donation date
        (3 months gap required)
        """
        if not self.last_donation_month or not self.last_donation_year:
            return True  # Never donated before

        try:
            from datetime import datetime, timedelta

            # Convert month name to number
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }

            last_donation_date = datetime(
                int(self.last_donation_year),
                month_map.get(self.last_donation_month, 1),
                1
            )

            # Check if 3 months (90 days) have passed
            three_months_later = last_donation_date + timedelta(days=90)
            return datetime.now() >= three_months_later

        except (ValueError, TypeError):
            return True  # If there's an error, assume can donate

    @property
    def next_donation_date(self):
        """Calculate when donor can donate next"""
        if not self.last_donation_month or not self.last_donation_year:
            return "Available now"

        try:
            from datetime import datetime, timedelta

            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }

            last_donation_date = datetime(
                int(self.last_donation_year),
                month_map.get(self.last_donation_month, 1),
                1
            )

            next_date = last_donation_date + timedelta(days=90)

            if datetime.now() >= next_date:
                return "Available now"
            else:
                return next_date.strftime("%d %B %Y")

        except (ValueError, TypeError):
            return "Available now"

    def save(self, *args, **kwargs):
        """Override save to ensure all declarations are properly set"""
        # Ensure all health declarations are True for active donors
        if self.is_active and not all([
            self.health_declaration,
            self.medication_declaration,
            self.consent_declaration
        ]):
            # You might want to handle this differently based on your business logic
            pass

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for this donor's profile"""
        from django.urls import reverse
        return reverse('donors:donor_profile', kwargs={'pk': self.pk})

    def __repr__(self):
        return f"<Donor: {self.full_name} ({self.blood_group}) - {self.phone_number}>"


class Recipient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    THANA_CHOICES = [
        ('Adabar', 'Adabar'),
        ('Badda', 'Badda'),
        ('Banani', 'Banani'),
        ('Baridhara', 'Baridhara'),
        ('Dhanmondi', 'Dhanmondi'),
        ('Gulshan', 'Gulshan'),
        ('Hatirjheel', 'Hatirjheel'),
        ('Kafrul', 'Kafrul'),
        ('Kalabagan', 'Kalabagan'),
        ('Khilgaon', 'Khilgaon'),
        ('Khilkhet', 'Khilkhet'),
        ('Mirpur', 'Mirpur'),
        ('Mohammadpur', 'Mohammadpur'),
        ('Motijheel', 'Motijheel'),
        ('New Market', 'New Market'),
        ('Old Dhaka', 'Old Dhaka'),
        ('Pallabi', 'Pallabi'),
        ('Ramna', 'Ramna'),
        ('Rampura', 'Rampura'),
        ('Sabujbagh', 'Sabujbagh'),
        ('Shah Ali', 'Shah Ali'),
        ('Sher-e-Bangla Nagar', 'Sher-e-Bangla Nagar'),
        ('Tejgaon', 'Tejgaon'),
        ('Uttara', 'Uttara'),
        ('Wari', 'Wari'),
    ]

    POST_OFFICE_CHOICES = [
        ('Dhaka GPO', 'Dhaka GPO'),
        ('Banani', 'Banani'),
        ('Dhanmondi', 'Dhanmondi'),
        ('Gulshan', 'Gulshan'),
        ('Mirpur', 'Mirpur'),
        ('Mohammadpur', 'Mohammadpur'),
        ('Motijheel', 'Motijheel'),
        ('New Market', 'New Market'),
        ('Old Dhaka', 'Old Dhaka'),
        ('Ramna', 'Ramna'),
        ('Tejgaon', 'Tejgaon'),
        ('Uttara', 'Uttara'),
        ('Wari', 'Wari'),
    ]

    DISTRICT_CHOICES = [
        ('Dhaka', 'Dhaka'),
    ]

    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+8801567890123'. Up to 15 digits allowed."
    )

    # Link to Django User model - NOW NULLABLE
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recipient_profile',
                                null=True, blank=True)

    # Keep these fields for backward compatibility during migration
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    house_holding_no = models.CharField(max_length=100)
    road_block = models.CharField(max_length=200)
    thana = models.CharField(max_length=50, choices=THANA_CHOICES)
    post_office = models.CharField(max_length=50, choices=POST_OFFICE_CHOICES)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES, default='Dhaka')

    # Optional fields
    age = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='recipient_images/', null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'

    def __str__(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name} - {self.blood_group}"
        else:
            return f"{self.first_name} {self.last_name} - {self.blood_group}"

    @property
    def full_name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        else:
            return f"{self.first_name} {self.last_name}"

    @property
    def user_email(self):
        if self.user:
            return self.user.email
        else:
            return self.email

    @property
    def full_address(self):
        return f"{self.house_holding_no}, {self.road_block}, {self.thana}, {self.post_office}, {self.district}"


class DonationHistory(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField(default=timezone.now)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, default="Dhaka, Bangladesh")
    blood_group = models.CharField(max_length=5)
    amount = models.IntegerField(default=450, help_text="Amount in ml")
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-donation_date']
        verbose_name = 'Donation History'
        verbose_name_plural = 'Donation Histories'

    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.donation_date.strftime('%Y-%m-%d')}"


class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    # Request details
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_group_needed = models.CharField(max_length=3, choices=Donor.BLOOD_GROUP_CHOICES)
    units_needed = models.PositiveIntegerField(default=1, help_text="Number of blood units needed")
    urgency_level = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')

    # Location details
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    thana = models.CharField(max_length=50, choices=Donor.THANA_CHOICES)
    district = models.CharField(max_length=50, default='Dhaka')

    # Request details
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField()
    medical_condition = models.CharField(max_length=200, blank=True)
    needed_by_date = models.DateTimeField()
    additional_notes = models.TextField(blank=True)

    # Contact information
    contact_person = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    alternative_contact = models.CharField(max_length=15, blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-urgency_level', '-created_at']
        verbose_name = 'Blood Request'
        verbose_name_plural = 'Blood Requests'
        indexes = [
            models.Index(fields=['blood_group_needed']),
            models.Index(fields=['thana']),
            models.Index(fields=['status']),
            models.Index(fields=['urgency_level']),
        ]

    def __str__(self):
        return f"{self.blood_group_needed} needed for {self.patient_name} at {self.hospital_name}"

    @property
    def is_urgent(self):
        return self.urgency_level in ['high', 'critical']

    @property
    def time_remaining(self):
        from datetime import timedelta
        remaining = self.needed_by_date - timezone.now()
        if remaining.total_seconds() < 0:
            return "Expired"
        elif remaining.days > 0:
            return f"{remaining.days} days"
        elif remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} hours"
        else:
            minutes = remaining.seconds // 60
            return f"{minutes} minutes"


class DonorResponse(models.Model):
    RESPONSE_CHOICES = [
        ('accept', 'Accept'),
        ('refuse', 'Refuse'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='responses')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='donor_responses')
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    response_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional notes for the response")

    # If accepted
    preferred_donation_time = models.DateTimeField(null=True, blank=True)
    availability_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['donor', 'blood_request']
        ordering = ['-response_date']
        verbose_name = 'Donor Response'
        verbose_name_plural = 'Donor Responses'

    def __str__(self):
        return f"{self.donor.full_name} - {self.response} - {self.blood_request.patient_name}"


class DonorPoints(models.Model):
    """
    Track RD Points for each donor
    """
    donor = models.OneToOneField(
        'Donor',
        on_delete=models.CASCADE,
        related_name='points'
    )
    total_points = models.PositiveIntegerField(default=0, help_text="Total RD Points earned")
    available_points = models.PositiveIntegerField(default=0, help_text="Available points for withdrawal")
    withdrawn_points = models.PositiveIntegerField(default=0, help_text="Total points withdrawn")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Donor Points"
        verbose_name_plural = "Donor Points"

    def __str__(self):
        return f"{self.donor.full_name} - {self.available_points} RD Points"

    def add_points(self, points, reason="Blood Donation"):
        """Add points to donor account"""
        self.total_points += points
        self.available_points += points
        self.save()

        # Create transaction record
        PointTransaction.objects.create(
            donor_points=self,
            transaction_type='earned',
            points=points,
            description=reason
        )

    def withdraw_points(self, points, method="SSL Commerce"):
        """Withdraw points from donor account"""
        if self.available_points >= points:
            self.available_points -= points
            self.withdrawn_points += points
            self.save()

            # Create transaction record
            PointTransaction.objects.create(
                donor_points=self,
                transaction_type='withdrawn',
                points=points,
                description=f"Withdrawal via {method}"
            )
            return True
        return False


class PointTransaction(models.Model):
    """
    Track all point transactions
    """
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('withdrawn', 'Withdrawn'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ]

    donor_points = models.ForeignKey(
        DonorPoints,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField(help_text="Positive for earned, negative for withdrawn")
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Point Transaction"
        verbose_name_plural = "Point Transactions"

    def __str__(self):
        return f"{self.donor_points.donor.full_name} - {self.transaction_type} {self.points} points"


class DonorBadge(models.Model):
    """
    Donor achievement badges
    """
    BADGE_TYPES = [
        ('first_donor', 'First Time Donor'),
        ('regular_donor', 'Regular Donor'),  # 2+ donations
        ('super_donor', 'Super Donor'),  # 5+ donations
        ('top_donor', 'Top Donor'),  # 10+ donations
        ('hero_donor', 'Hero Donor'),  # 20+ donations
        ('lifesaver', 'Life Saver'),  # 50+ donations
    ]

    donor = models.ForeignKey(
        'Donor',
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    earned_date = models.DateTimeField(auto_now_add=True)
    donation_count_when_earned = models.PositiveIntegerField()

    class Meta:
        unique_together = ['donor', 'badge_type']
        ordering = ['-earned_date']
        verbose_name = "Donor Badge"
        verbose_name_plural = "Donor Badges"

    def __str__(self):
        return f"{self.donor.full_name} - {self.get_badge_type_display()}"

    @property
    def badge_icon(self):
        """Return appropriate icon for badge type"""
        icons = {
            'first_donor': 'fa-heart',
            'regular_donor': 'fa-medal',
            'super_donor': 'fa-trophy',
            'top_donor': 'fa-crown',
            'hero_donor': 'fa-star',
            'lifesaver': 'fa-award'
        }
        return icons.get(self.badge_type, 'fa-medal')

    @property
    def badge_color(self):
        """Return appropriate color for badge type"""
        colors = {
            'first_donor': 'badge-success',
            'regular_donor': 'badge-primary',
            'super_donor': 'badge-warning',
            'top_donor': 'badge-danger',
            'hero_donor': 'badge-dark',
            'lifesaver': 'badge-gold'
        }
        return colors.get(self.badge_type, 'badge-primary')


class WithdrawalRequest(models.Model):
    """
    Handle point withdrawal requests via SSL Commerce
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(
        'Donor',
        on_delete=models.CASCADE,
        related_name='withdrawal_requests'
    )
    points_requested = models.PositiveIntegerField()
    amount_bdt = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in BDT")
    ssl_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    # Bank/Payment details (will be added when SSL Commerce integration is active)
    payment_method = models.CharField(max_length=50, default='SSL Commerce')
    account_details = models.JSONField(blank=True, null=True)  # Store encrypted payment details

    class Meta:
        ordering = ['-requested_at']
        verbose_name = "Withdrawal Request"
        verbose_name_plural = "Withdrawal Requests"

    def __str__(self):
        return f"{self.donor.full_name} - {self.points_requested} points ({self.status})"

    @property
    def conversion_rate(self):
        """1 RD Point = 1 BDT (can be made configurable)"""
        return 1.0


# Helper function to update donation history and award points/badges
def process_donation_rewards(donor):
    """
    Process rewards after a successful blood donation
    """
    # Get or create points account
    points_account, created = DonorPoints.objects.get_or_create(donor=donor)

    # Award 100 points for donation
    points_account.add_points(100, "Blood Donation")

    # Count completed donations
    from .models import DonationHistory
    donation_count = DonationHistory.objects.filter(
        donor=donor,
        status='completed'
    ).count()

    # Award badges based on donation count
    badge_thresholds = [
        (1, 'first_donor'),
        (2, 'regular_donor'),
        (5, 'super_donor'),
        (10, 'top_donor'),
        (20, 'hero_donor'),
        (50, 'lifesaver'),
    ]

    for threshold, badge_type in badge_thresholds:
        if donation_count >= threshold:
            # Check if badge already exists
            existing_badge = DonorBadge.objects.filter(
                donor=donor,
                badge_type=badge_type
            ).first()

            if not existing_badge:
                DonorBadge.objects.create(
                    donor=donor,
                    badge_type=badge_type,
                    donation_count_when_earned=donation_count
                )

                # Award bonus points for milestone badges
                if badge_type in ['super_donor', 'top_donor', 'hero_donor', 'lifesaver']:
                    bonus_points = {
                        'super_donor': 500,
                        'top_donor': 1000,
                        'hero_donor': 2000,
                        'lifesaver': 5000,
                    }
                    points_account.add_points(
                        bonus_points.get(badge_type, 0),
                        f"Milestone Badge: {badge_type.replace('_', ' ').title()}"
                    )