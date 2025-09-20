from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from .models import *
from .models import Recipient
from django.core.exceptions import ValidationError
from .utils import *


class DonorRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-control',
            'id': 'firstName'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-control',
            'id': 'lastName'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-control',
            'id': 'email'
        })
    )

    # Password fields
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create Password',
            'class': 'form-control',
            'id': 'password'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
            'id': 'confirmPassword'
        })
    )

    # Address fields that match HTML
    house_holding_no = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'House Holding No',
            'class': 'form-control',
            'id': 'houseHolding'
        })
    )
    road_block = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Road/Block',
            'class': 'form-control',
            'id': 'roadBlock'
        })
    )
    thana = forms.ChoiceField(
        choices=[
            ('', 'Select Thana'),
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
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'thana'
        })
    )
    post_office = forms.ChoiceField(
        choices=[
            ('', 'Select Post Office'),
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
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'postOffice'
        })
    )
    district = forms.CharField(
        max_length=50,
        initial='Dhaka',
        required=True,
        widget=forms.Select(
            choices=[('', 'Select District'), ('Dhaka', 'Dhaka')],
            attrs={
                'class': 'form-control',
                'id': 'district'
            }
        )
    )

    # Weight field (added as it's in HTML but not in original form)
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=1,
        min_value=50,
        required=True,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Weight in kg',
            'min': '50',
            'step': '0.1',
            'class': 'form-control',
            'id': 'weight'
        })
    )

    # Health declaration fields
    health_declaration = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput()
    )
    medication_declaration = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput()
    )
    consent_declaration = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = Donor
        fields = [
            'phone_number', 'age', 'blood_group',
            'last_donation_month', 'last_donation_year', 'profile_image'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control',
                'id': 'phone'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Age (18-65)',
                'class': 'form-control',
                'min': 18,
                'max': 65,
                'id': 'age'
            }),
            'blood_group': forms.Select(
                choices=[
                    ('', 'Select Your Blood Group'),
                    ('A+', 'A+'),
                    ('A-', 'A-'),
                    ('B+', 'B+'),
                    ('B-', 'B-'),
                    ('AB+', 'AB+'),
                    ('AB-', 'AB-'),
                    ('O+', 'O+'),
                    ('O-', 'O-'),
                ],
                attrs={
                    'class': 'form-control',
                    'id': 'bloodGroup'
                }
            ),
            'last_donation_month': forms.Select(
                choices=[
                    ('', 'Select Month'),
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
                ],
                attrs={
                    'class': 'form-control',
                    'id': 'lastDonationMonth'
                }
            ),
            'last_donation_year': forms.Select(
                choices=[
                    ('', 'Select Year'),
                    ('2024', '2024'),
                    ('2023', '2023'),
                    ('2022', '2022'),
                    ('2021', '2021'),
                    ('2020', '2020'),
                    ('2019', '2019'),
                    ('2018', '2018'),
                    ('2017', '2017'),
                    ('2016', '2016'),
                    ('2015', '2015'),
                ],
                attrs={
                    'class': 'form-control',
                    'id': 'lastDonationYear'
                }
            ),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'profileImage',
                'style': 'display: none;'
            })
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if Donor.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("A donor with this phone number already exists.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size should not exceed 5MB.")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 18 or age > 65):
            raise forms.ValidationError("Age must be between 18 and 65 years.")
        return age

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and weight < 50:
            raise forms.ValidationError("Minimum weight of 50kg is required for safe blood donation.")
        return weight

    def clean_last_donation_year(self):
        year = self.cleaned_data.get('last_donation_year')
        if year:
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if year_int > current_year or year_int < (current_year - 10):
                    raise forms.ValidationError("Please enter a valid year.")
            except ValueError:
                raise forms.ValidationError("Year must be a number.")
        return year


    def save(self, commit=True):
        if commit:
            # Create the User first
            user = User.objects.create_user(
                username=self.cleaned_data['email'],  # Use email as username
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )

            # Create the Donor profile
            donor = super().save(commit=False)
            donor.user = user

            # Set additional fields from form
            if hasattr(donor, 'weight'):
                donor.weight = self.cleaned_data['weight']
            if hasattr(donor, 'house_holding_no'):
                donor.house_holding_no = self.cleaned_data['house_holding_no']
            if hasattr(donor, 'road_block'):
                donor.road_block = self.cleaned_data['road_block']
            if hasattr(donor, 'thana'):
                donor.thana = self.cleaned_data['thana']
            if hasattr(donor, 'post_office'):
                donor.post_office = self.cleaned_data['post_office']
            if hasattr(donor, 'district'):
                donor.district = self.cleaned_data['district']

            donor.save()

            # Send welcome email
            send_donor_welcome_email(donor)

            # Send admin notification
            send_admin_notification('donor', {
                'name': donor.full_name,
                'email': donor.email,
                'blood_group': donor.blood_group,
                'location': f"{donor.thana}, {donor.district}",
                'phone': donor.phone_number,
            })

            return donor
        else:
            return super().save(commit=False)

class DonorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'phone_number', 'age', 'blood_group',
            'house_holding_no', 'road_block', 'thana', 'post_office', 'district',
            'last_donation_month', 'last_donation_year', 'profile_image', 'weight'
        ]
        # Removed non-existent fields: first_name, last_name, address, state, pincode

        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 65}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'house_holding_no': forms.TextInput(attrs={'class': 'form-control'}),
            'road_block': forms.TextInput(attrs={'class': 'form-control'}),
            'thana': forms.Select(attrs={'class': 'form-control'}),
            'post_office': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 50, 'step': 0.1}),
            'last_donation_month': forms.Select(attrs={'class': 'form-control'}),
            'last_donation_year': forms.Select(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generate year choices
        current_year = datetime.now().year
        year_choices = [('', 'Select Year')] + [(str(year), str(year)) for year in
                                                range(current_year, current_year - 6, -1)]
        self.fields['last_donation_year'].widget = forms.Select(
            choices=year_choices,
            attrs={'class': 'form-control'}
        )

        # Month choices
        month_choices = [
            ('', 'Select Month'),
            ('January', 'January'), ('February', 'February'), ('March', 'March'),
            ('April', 'April'), ('May', 'May'), ('June', 'June'),
            ('July', 'July'), ('August', 'August'), ('September', 'September'),
            ('October', 'October'), ('November', 'November'), ('December', 'December')
        ]

        self.fields['last_donation_month'].widget = forms.Select(
            choices=month_choices,
            attrs={'class': 'form-control'}
        )

        # Add thana choices
        thana_choices = [
            ('', 'Select Thana'),
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

        self.fields['thana'].widget = forms.Select(
            choices=thana_choices,
            attrs={'class': 'form-control'}
        )

        # Add post office choices
        post_office_choices = [
            ('', 'Select Post Office'),
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

        self.fields['post_office'].widget = forms.Select(
            choices=post_office_choices,
            attrs={'class': 'form-control'}
        )

        # Add blood group choices
        blood_group_choices = [
            ('', 'Select Your Blood Group'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ]

        self.fields['blood_group'].widget = forms.Select(
            choices=blood_group_choices,
            attrs={'class': 'form-control'}
        )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Exclude current instance from duplicate check
        if self.instance and self.instance.pk:
            if Donor.objects.filter(phone_number=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A donor with this phone number already exists.")
        else:
            if Donor.objects.filter(phone_number=phone).exists():
                raise forms.ValidationError("A donor with this phone number already exists.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size should not exceed 5MB.")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 18 or age > 65):
            raise forms.ValidationError("Age must be between 18 and 65 years.")
        return age

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and weight < 50:
            raise forms.ValidationError("Minimum weight of 50kg is required for safe blood donation.")
        return weight

    def clean_last_donation_year(self):
        year = self.cleaned_data.get('last_donation_year')
        if year:
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if year_int > current_year or year_int < (current_year - 10):
                    raise forms.ValidationError("Please enter a valid year.")
            except ValueError:
                raise forms.ValidationError("Year must be a number.")
        return year

class DonorResponseForm(forms.ModelForm):
    class Meta:
        model = DonorResponse
        fields = ['response', 'notes', 'preferred_donation_time', 'availability_notes']
        widgets = {
            'response': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes or comments...'
            }),
            'preferred_donation_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'availability_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'When are you available for donation?'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['response'].choices = [
            ('accept', 'Accept - I can donate'),
            ('refuse', 'Refuse - Cannot donate at this time')
        ]
        self.fields['notes'].required = False
        self.fields['preferred_donation_time'].required = False
        self.fields['availability_notes'].required = False

class RecipientRegistrationForm(forms.ModelForm):
    # Add user fields
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        required=True,
        help_text="Password must be at least 8 characters long"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text="Enter the same password again"
    )

    class Meta:
        model = Recipient
        fields = [
            'phone_number', 'blood_group', 'house_holding_no',
            'road_block', 'thana', 'post_office', 'district',
            'age', 'image'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'min': 1, 'max': 120}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'thana': forms.Select(attrs={'class': 'form-select'}),
            'post_office': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords don't match.")
        return confirm_password

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if Recipient.objects.filter(phone_number=phone).exists():
            raise ValidationError("A recipient with this phone number already exists.")
        return phone

    def save(self, commit=True):
        if commit:
            # Create the User first
            user = User.objects.create_user(
                username=self.cleaned_data['email'],  # Use email as username
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )

            # Create the Recipient profile
            recipient = super().save(commit=False)
            recipient.user = user
            recipient.save()

            # Send welcome email
            send_recipient_welcome_email(recipient)

            # Send admin notification
            send_admin_notification('recipient', {
                'name': recipient.full_name,
                'email': recipient.user_email,
                'blood_group': recipient.blood_group,
                'location': f"{recipient.thana}, {recipient.district}",
                'phone': recipient.phone_number,
            })

            return recipient
        else:
            return super().save(commit=False)