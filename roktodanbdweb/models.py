from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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