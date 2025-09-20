from .models import *
from django.contrib.auth import logout as auth_logout
from django.views import View
from .utils import send_registration_email, send_admin_notification
import logging
from django.contrib.auth import authenticate, login
from .forms import RecipientRegistrationForm, DonorResponseForm, DonorRegistrationForm
from .models import Recipient
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Donor, DonationHistory, DonorPoints, DonorBadge, PointTransaction


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
            try:
                donor = form.save()
                messages.success(
                    request,
                    f'Registration successful! Welcome {donor.full_name}. '
                    'A confirmation email has been sent to your email address.'
                )
                return redirect('success')
            except Exception as e:
                logger.error(f"Donor registration error: {str(e)}")
                messages.error(request, 'Registration failed. Please try again.')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
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
def donor_history(request):
    """
    Display donor's blood donation history
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        # Redirect to donor registration if no donor profile exists
        return redirect('donor_registration')

    # Get all donation history for this donor
    donation_history = DonationHistory.objects.filter(donor=donor)

    # Apply filters if provided
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status_filter = request.GET.get('status')

    if from_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            donation_history = donation_history.filter(donation_date__date__gte=from_date)
        except ValueError:
            pass

    if to_date:
        try:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            donation_history = donation_history.filter(donation_date__date__lte=to_date)
        except ValueError:
            pass

    if status_filter:
        donation_history = donation_history.filter(status=status_filter)

    # Calculate statistics
    total_donations = donation_history.filter(status='completed').count()
    lives_saved = total_donations * 3  # Typically 1 donation saves 3 lives

    # Calculate days since last donation
    last_donation = donation_history.filter(status='completed').first()
    days_since_last = None
    if last_donation:
        days_since_last = (timezone.now().date() - last_donation.donation_date.date()).days

    context = {
        'donor': donor,
        'donation_history': donation_history,
        'total_donations': total_donations,
        'lives_saved': lives_saved,
        'days_since_last': days_since_last,
    }

    return render(request, 'donor_history.html', context)


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
                    f'Registration successful! Welcome {recipient.full_name}. '
                    'A confirmation email has been sent to your email address.'
                )
                return redirect('login')  # Redirect to login page
            except Exception as e:
                logger.error(f"Recipient registration error: {str(e)}")
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


@login_required
def matching(request):
    """
    Matching page for donors to see blood requests and respond
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found. Please complete your registration.")
        return redirect('donor_registration')

    # Get compatible blood requests
    compatible_requests = BloodRequest.objects.filter(
        blood_group_needed=donor.blood_group,
        thana=donor.thana,
        status='active'
    ).exclude(
        # Exclude requests the donor has already responded to
        donor_responses__donor=donor
    ).order_by('-urgency_level', '-created_at')

    # Get recent matches (requests the donor has responded to)
    recent_responses = DonorResponse.objects.filter(
        donor=donor
    ).select_related('blood_request', 'blood_request__recipient').order_by('-response_date')[:10]

    # Get statistics
    total_responses = DonorResponse.objects.filter(donor=donor).count()
    accepted_responses = DonorResponse.objects.filter(donor=donor, response='accept').count()

    context = {
        'donor': donor,
        'compatible_requests': compatible_requests,
        'recent_responses': recent_responses,
        'total_responses': total_responses,
        'accepted_responses': accepted_responses,
    }

    return render(request, 'matching.html', context)


@login_required
def respond_to_request(request, request_id):
    """
    Handle donor response to blood request
    """
    try:
        donor = get_object_or_404(Donor, user=request.user)
        blood_request = get_object_or_404(BloodRequest, id=request_id, status='active')
    except (Donor.DoesNotExist, BloodRequest.DoesNotExist):
        messages.error(request, "Request not found or invalid.")
        return redirect('matching')

    # Check if donor has already responded
    existing_response = DonorResponse.objects.filter(
        donor=donor,
        blood_request=blood_request
    ).first()

    if existing_response:
        messages.warning(request, "You have already responded to this request.")
        return redirect('matching')

    if request.method == 'POST':
        form = DonorResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.donor = donor
            response.blood_request = blood_request
            response.save()

            if response.response == 'accept':
                messages.success(request,
                                 "Thank you for accepting this blood donation request! The recipient will be notified.")
                # Here you could send email/SMS notification
            else:
                messages.info(request, "Response recorded. Thank you for your time.")

            return redirect('matching')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DonorResponseForm()

    context = {
        'donor': donor,
        'blood_request': blood_request,
        'form': form,  # Make sure this is included
    }

    return render(request, 'respond_to_request.html', context)


def rewards(request):
    """
    Rewards page showing points, badges, and withdrawal options
    """
    context = {
        'page_title': 'Rewards & Points',
    }

    if request.user.is_authenticated and hasattr(request.user, 'donor'):
        donor = request.user.donor

        # Get or create points account
        points_account, created = DonorPoints.objects.get_or_create(donor=donor)

        # Count completed donations
        total_donations = DonationHistory.objects.filter(
            donor=donor,
            status='completed'
        ).count()

        # ✅ Calculate lives saved here
        lives_saved = total_donations * 3

        # Earned badges
        earned_badges = DonorBadge.objects.filter(donor=donor).order_by('-earned_date')

        # Current highest badge
        current_badge = "New Donor"
        if earned_badges.exists():
            latest_badge = earned_badges.first()
            current_badge = latest_badge.get_badge_type_display()

        # Next milestone
        next_milestone = None
        milestones = [
            {'count': 1, 'name': 'First Time Donor'},
            {'count': 2, 'name': 'Regular Donor'},
            {'count': 5, 'name': 'Super Donor'},
            {'count': 10, 'name': 'Top Donor'},
            {'count': 20, 'name': 'Hero Donor'},
            {'count': 50, 'name': 'Life Saver'},
        ]
        for milestone in milestones:
            if total_donations < milestone['count']:
                next_milestone = milestone
                break

        # Recent transactions
        recent_transactions = PointTransaction.objects.filter(
            donor_points=points_account
        ).order_by('-created_at')[:10]

        # ✅ Badge existence flags for template
        badge_flags = {
            "has_first_donor_badge": DonorBadge.objects.filter(donor=donor, badge_type="first_donor").exists(),
            "has_regular_donor_badge": DonorBadge.objects.filter(donor=donor, badge_type="regular_donor").exists(),
            "has_super_donor_badge": DonorBadge.objects.filter(donor=donor, badge_type="super_donor").exists(),
            "has_top_donor_badge": DonorBadge.objects.filter(donor=donor, badge_type="top_donor").exists(),
            "has_hero_donor_badge": DonorBadge.objects.filter(donor=donor, badge_type="hero_donor").exists(),
            "has_lifesaver_badge": DonorBadge.objects.filter(donor=donor, badge_type="lifesaver").exists(),
        }

        context.update({
            'donor': donor,
            'total_donations': total_donations,
            'lives_saved': lives_saved,
            'current_badge': current_badge,
            'next_milestone': next_milestone,
            'recent_transactions': recent_transactions,
            'earned_badges': earned_badges,
            **badge_flags,  # add all badge flags
        })

    return render(request, 'rewards.html', context)


@login_required
def withdraw_points(request):
    """
    Handle point withdrawal requests (currently disabled)
    """
    if not hasattr(request.user, 'donor'):
        messages.error(request, "Donor profile not found.")
        return redirect('rewards')

    donor = request.user.donor
    points_account, created = DonorPoints.objects.get_or_create(donor=donor)

    if request.method == 'POST':
        points_to_withdraw = int(request.POST.get('points_to_withdraw', 0))

        if points_to_withdraw < 100:
            messages.error(request, "Minimum withdrawal amount is 100 RD Points.")
            return redirect('rewards')

        if points_to_withdraw > points_account.available_points:
            messages.error(request, "Insufficient points for withdrawal.")
            return redirect('rewards')

        # Create withdrawal request (SSL Commerce integration will be added later)
        withdrawal_request = WithdrawalRequest.objects.create(
            donor=donor,
            points_requested=points_to_withdraw,
            amount_bdt=points_to_withdraw * 1.0,  # 1:1 conversion rate
            status='pending'
        )

        messages.info(
            request,
            f"Withdrawal request for {points_to_withdraw} RD Points has been submitted. "
            "SSL Commerce integration will be available soon."
        )

    return redirect('rewards')


# Helper function to award points and badges after donation
def award_donation_rewards(donor):
    """
    Award points and badges after successful blood donation
    Call this function after a donation is recorded
    """
    # Get or create points account
    points_account, created = DonorPoints.objects.get_or_create(donor=donor)

    # Award 100 points for donation
    points_account.add_points(100, "Blood Donation")

    # Count completed donations
    donation_count = DonationHistory.objects.filter(
        donor=donor,
        status='completed'
    ).count()

    # Award badges based on donation count
    badge_thresholds = [
        (1, 'first_donor', 0),
        (2, 'regular_donor', 200),
        (5, 'super_donor', 500),
        (10, 'top_donor', 1000),
        (20, 'hero_donor', 2000),
        (50, 'lifesaver', 5000),
    ]

    for threshold, badge_type, bonus_points in badge_thresholds:
        if donation_count >= threshold:
            # Check if badge already exists
            existing_badge = DonorBadge.objects.filter(
                donor=donor,
                badge_type=badge_type
            ).first()

            if not existing_badge:
                # Create new badge
                DonorBadge.objects.create(
                    donor=donor,
                    badge_type=badge_type,
                    donation_count_when_earned=donation_count
                )

                # Award bonus points for milestone badges
                if bonus_points > 0:
                    points_account.add_points(
                        bonus_points,
                        f"Milestone Badge: {badge_type.replace('_', ' ').title()}"
                    )

    return points_account, donation_count