from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from .models import *


class DonorRegistrationForm(forms.ModelForm):
    # Add password fields for user creation
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'})
    )

    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'phone_number', 'email', 'address',
            'age', 'blood_group', 'district', 'state', 'pincode',
            'last_donation_month', 'last_donation_year', 'profile_image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First',
                'class': 'form-control',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-control',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Number',
                'class': 'form-control',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Mail_id',
                'class': 'form-control',
                'required': True
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Choose your current location',
                'class': 'form-control',
                'required': True
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Age',
                'class': 'form-control',
                'min': 18,
                'max': 65,
                'required': True
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'district': forms.TextInput(attrs={
                'placeholder': 'District',
                'class': 'form-control',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'placeholder': 'State/Division',
                'class': 'form-control',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'placeholder': 'Postal Code',
                'class': 'form-control',
                'required': True
            }),
            'last_donation_month': forms.TextInput(attrs={
                'placeholder': 'Month',
                'class': 'form-control'
            }),
            'last_donation_year': forms.TextInput(attrs={
                'placeholder': 'Year',
                'class': 'form-control'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Donor.objects.filter(email=email).exists():
            raise forms.ValidationError("A donor with this email already exists.")
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


class DonorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'phone_number', 'address',
            'age', 'blood_group', 'district', 'state', 'pincode',
            'last_donation_month', 'last_donation_year', 'profile_image'
        ]
        # Exclude email from update form as mentioned in requirements

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 65}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
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


# Form for searching donors
class DonorSearchForm(forms.Form):
    blood_group = forms.ChoiceField(
        choices=[('', 'All Blood Groups')] + Donor.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter district'
        })
    )
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter state/division'
        })
    )


# Custom login form using email
class DonorLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )


# Form for updating just basic info (without sensitive fields)
class DonorBasicUpdateForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'phone_number', 'address',
            'age', 'district', 'state', 'pincode', 'profile_image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 65}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }


class RecipientRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'required': True
        }),
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = Recipient
        fields = [
            'first_name', 'last_name', 'phone_number', 'blood_group',
            'email', 'house_holding_no', 'road_block', 'thana',
            'post_office', 'district', 'age', 'image'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'required': True
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'house_holding_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'House Holding No',
                'required': True
            }),
            'road_block': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Road/Block',
                'required': True
            }),
            'thana': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'post_office': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': 1,
                'max': 120
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove any spaces, dashes, or parentheses
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if Recipient.objects.filter(email=email).exists():
                raise forms.ValidationError("A recipient with this email already exists.")
        return email

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 1 or age > 120):
            raise forms.ValidationError("Please enter a valid age between 1 and 120.")
        return age

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords don't match.")
        return confirm_password

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Add additional password validation if needed
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            # You can add more validation rules here (e.g., uppercase, numbers, special chars)
        return password