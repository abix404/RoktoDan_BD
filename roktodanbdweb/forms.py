from django import forms
from .models import Donor

class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Mail_id'}),
            'address': forms.TextInput(attrs={'placeholder': 'Choose your current location'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'last_donation_month': forms.TextInput(attrs={'placeholder': 'Month'}),
            'last_donation_year': forms.TextInput(attrs={'placeholder': 'Year'}),
        }