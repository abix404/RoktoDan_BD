from .forms import DonorRegistrationForm
from .models import *
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views import View
from .utils import send_registration_email, send_admin_notification
import logging
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecipientRegistrationForm
from .models import Recipient

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')
# Create your views here.

def about_us(request):
    return render(request, 'about_us.html')

def donor_credit(request):
    return render(request, 'donor_credit.html')

def donation_history(request):
    return render(request, 'donation_history.html')


@login_required
def logout(request):
    """
    Logs out the user and shows the animated logout page
    """
    auth_logout(request)
    return render(request, 'logout.html')

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('registration_success')
    else:
        form = DonorRegistrationForm()

    return render(request, 'register_donor.html', {'form': form})


def registration_success(request):
    return render(request, 'success.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # This will be email or phone
        password = request.POST.get('password')

        print(f"Login attempt with: {username}")  # Debug

        user = None

        # Try to authenticate with email (most common)
        if '@' in username:
            user = authenticate(request, username=username, password=password)
            print(f"Email authentication result: {user}")
        else:
            # If it's not an email, try to find user by phone number
            try:
                recipient = Recipient.objects.get(phone_number=username)
                user = authenticate(request, username=recipient.user.email, password=password)
                print(f"Phone authentication result: {user}")
            except Recipient.DoesNotExist:
                print("No recipient found with this phone number")
                # Try direct username authentication as fallback
                user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"Login successful for user: {user}")

            # Check if user has a recipient profile
            if hasattr(user, 'recipient_profile'):
                messages.success(request, f'Welcome back, {user.recipient_profile.full_name}!')
                return redirect('/')  # or recipient dashboard
            else:
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('/')  # regular user/donor dashboard
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid email/phone or password')

    return render(request, 'login.html')

def quick_register_recipient(request):
    return render(request, 'quick_register_recipient.html')


def register_recipient(request):
    if request.method == 'POST':
        form = RecipientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                recipient = form.save()
                messages.success(
                    request,
                    f'Registration successful! Welcome {recipient.full_name}. You can now log in.'
                )
                return redirect('login')  # Redirect to login page
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = field.replace("_", " ").title()
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = RecipientRegistrationForm()

    return render(request, 'register_recipient.html', {'form': form})

# Success page view
def recipient_success(request):
    return render(request, 'success.html')


class RecipientRegistrationView(View):
    template_name = 'register_recipient.html'
    form_class = RecipientRegistrationForm

    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'title': 'Register as Recipient'
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            try:
                recipient = form.save()

                # Send confirmation email to recipient
                email_sent = send_registration_email(recipient)

                # Send notification to admin
                send_admin_notification(recipient)

                # Success message
                if email_sent:
                    messages.success(
                        request,
                        f'Registration successful! Welcome {recipient.full_name}. '
                        f'A confirmation email has been sent to {recipient.email}.'
                    )
                else:
                    messages.success(
                        request,
                        f'Registration successful! Welcome {recipient.full_name}. '
                        f'However, we could not send the confirmation email. Please check your email address.'
                    )

                logger.info(f"New recipient registered: {recipient.full_name} ({recipient.email})")
                return redirect('recipient_success')

            except Exception as e:
                logger.error(f"Registration failed: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')

        context = {
            'form': form,
            'title': 'Register as Recipient'
        }
        return render(request, self.template_name, context)