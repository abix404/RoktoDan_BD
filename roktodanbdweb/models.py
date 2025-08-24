from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.utils import timezone

user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='donor',
    null=True,
    blank=True,
    help_text="Associated user account"
)

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