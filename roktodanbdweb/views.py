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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Donor

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about_us(request):
    return render(request, 'about_us.html')


def matching(request):
    return render(request, 'matching.html')
def registration(request):
    return render(request, 'registration.html')
def track_requests(request):
     return render(request, 'track-requests.html')
def rewards(request):
    return render(request, 'rewards.html')

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = DonorRegistrationForm()

    return render(request, 'register_donor.html', {'form': form})


def registration_success(request):
    return render(request, 'success.html')

@login_required
def donor_dashboard(request):
    """
    Donor dashboard view - shows donor profile and stats
    """
    try:
        # Get the donor profile for the logged-in user
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found. Please complete your registration.")
        return redirect('donor_registration')

    # Calculate donation statistics
    total_donations = calculate_total_donations(donor)
    lives_saved = total_donations * 3  # Assuming each donation saves 3 lives

    # Get recent activities (you can implement this based on your activity model)
    recent_activities = get_recent_activities(donor)

    context = {
        'donor': donor,
        'total_donations': total_donations,
        'lives_saved': lives_saved,
        'recent_activities': recent_activities,
    }

    return render(request, 'donors/donor_dashboard.html', context)


def calculate_total_donations(donor):
    """
    Calculate total number of donations based on donation history
    This is a simple calculation - you might want to implement a more sophisticated system
    """
    if not donor.last_donation_month or not donor.last_donation_year:
        return 0

    try:
        # This is a simplified calculation
        # In a real system, you'd have a separate DonationHistory model
        current_year = datetime.now().year
        last_donation_year = int(donor.last_donation_year)

        # Rough estimate based on eligibility (can donate every 3 months)
        years_since_first_donation = current_year - last_donation_year + 1
        estimated_donations = min(years_since_first_donation * 4, 20)  # Cap at 20

        return max(1, estimated_donations) if donor.last_donation_year else 0
    except (ValueError, TypeError):
        return 0


def get_recent_activities(donor):
    """
    Get recent activities for the donor
    This is a placeholder - implement based on your activity tracking system
    """
    activities = []

    # Example activities - replace with actual data from your models
    if donor.last_updated:
        time_diff = timezone.now() - donor.last_updated
        if time_diff.days < 7:
            activities.append({
                'icon': 'fa-edit',
                'message': 'Profile updated',
                'timestamp': donor.last_updated
            })

    if donor.registration_date:
        activities.append({
            'icon': 'fa-user-plus',
            'message': 'Joined RoktoDan BD',
            'timestamp': donor.registration_date
        })

    # You can add more activities like:
    # - Blood donation requests responded to
    # - Emergency requests
    # - Profile views
    # - etc.

    return activities[:5]  # Return last 5 activities


@login_required
def donor_profile_update(request):
    """
    Handle donor profile updates
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    if request.method == 'POST':
        # Handle form submission
        from .forms import DonorProfileUpdateForm
        form = DonorProfileUpdateForm(request.POST, request.FILES, instance=donor)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('donor_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        from .forms import DonorProfileUpdateForm
        form = DonorProfileUpdateForm(instance=donor)

    context = {
        'form': form,
        'donor': donor,
    }

    return render(request, 'donors/profile_update.html', context)


@login_required
def blood_request_list(request):
    """
    Show blood requests that match donor's blood group
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    # This would fetch blood requests from a BloodRequest model
    # For now, it's a placeholder
    context = {
        'donor': donor,
        'requests': [],  # Replace with actual blood requests
    }

    return render(request, 'donors/blood_requests.html', context)


@login_required
def donation_history(request):
    """
    Show donor's donation history
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    # This would fetch actual donation records from a DonationHistory model
    # For now, using the basic last donation info
    donation_records = []

    if donor.last_donation_month and donor.last_donation_year:
        donation_records.append({
            'date': f"{donor.last_donation_month} {donor.last_donation_year}",
            'location': 'Blood Bank',  # Placeholder
            'blood_group': donor.blood_group,
            'status': 'Completed'
        })

    context = {
        'donor': donor,
        'donation_records': donation_records,
        'total_donations': len(donation_records),
    }

    return render(request, 'donors/donation_history.html', context)


@login_required
def emergency_requests(request):
    """
    Show emergency blood requests
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    # This would fetch urgent blood requests from database
    # Filter by compatible blood groups and location
    emergency_requests = []  # Replace with actual emergency requests

    context = {
        'donor': donor,
        'emergency_requests': emergency_requests,
    }

    return render(request, 'donors/emergency_requests.html', context)

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


@login_required
def logout(request):
    """
    Logs out the user and shows the animated logout page
    """
    auth_logout(request)
    return render(request, 'logout.html')


def find_blood(request):
    """
    Handle Find Blood functionality:
    - Show quick login for non-authenticated users
    - Show search form and results for authenticated users
    """

    # For non-authenticated users, show the login page
    if not request.user.is_authenticated:
        return render(request, 'find_blood.html')

    # For authenticated users, handle blood search
    donors = None

    # Check if search parameters are provided
    blood_group = request.GET.get('blood_group')
    thana = request.GET.get('thana')
    post_office = request.GET.get('post_office')
    district = request.GET.get('district')

    # If all search parameters are provided, search for donors
    if all([blood_group, thana, post_office, district]):
        donors = Donor.objects.filter(
            blood_group=blood_group,
            thana=thana,
            post_office=post_office,
            district=district,
            is_active=True,
            is_available=True
        ).select_related('user').order_by('-registration_date')

        # Optional: Filter by donors who can actually donate (based on last donation date)
        # available_donors = [donor for donor in donors if donor.can_donate]
        # donors = available_donors

        # Add success message if donors found
        if donors.exists():
            messages.success(request, f'Found {donors.count()} available donor(s) in your area!')
        else:
            messages.warning(request, 'No donors found matching your criteria. Try searching in nearby areas.')

    # If user just logged in via social auth, create recipient profile automatically
    if request.user.is_authenticated and not hasattr(request.user, 'recipient_profile'):
        try:
            from .models import Recipient
            # Auto-create recipient profile for quick login users
            recipient = Recipient.objects.create(
                user=request.user,
                first_name=request.user.first_name or 'User',
                last_name=request.user.last_name or '',
                email=request.user.email,
                phone_number='',  # Will need to be updated later
                blood_group='',  # Will be filled when they search
                house_holding_no='',
                road_block='',
                thana='',
                post_office='',
                district='Dhaka'
            )
            messages.info(request, 'Welcome! Your recipient profile has been created. You can update it later.')
        except Exception as e:
            # Handle any errors in profile creation
            pass

    context = {
        'donors': donors,
        'search_params': {
            'blood_group': blood_group,
            'thana': thana,
            'post_office': post_office,
            'district': district,
        }
    }

    return render(request, 'find_blood.html', context)


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
