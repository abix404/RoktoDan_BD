from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.models import User

user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recipient_profile', null=True, blank=True)

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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(65)]
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    last_donation_month = models.CharField(max_length=20, blank=True, null=True)
    last_donation_year = models.CharField(max_length=4, blank=True, null=True)
    profile_image = models.ImageField(upload_to='donor_images/', blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.blood_group})"


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
        message="Phone number must be entered in the format: '+880199999'. Up to 15 digits allowed."
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