from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout as auth_logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    Donor, Recipient, DonationHistory, DonorPoints, DonorBadge,
    PointTransaction, BloodRequest, DonorResponse
)
from .forms import (
    RecipientRegistrationForm, DonorResponseForm, DonorRegistrationForm
)
from .utils import (
    send_registration_email, send_admin_notification,
    send_donor_response_notification, send_blood_request_email_to_donor
)

logger = logging.getLogger(__name__)


# ==================== PUBLIC VIEWS ====================

def home(request):
    """Home page view"""
    return render(request, 'home.html')


def about_us(request):
    """About us page view"""
    return render(request, 'about_us.html')


def registration(request):
    """Registration options page"""
    return render(request, 'registration.html')


def registration_success(request):
    """Registration success page"""
    return render(request, 'success.html')


def recipient_success(request):
    """Recipient registration success page"""
    return render(request, 'success.html')


# ==================== AUTHENTICATION ====================

def user_login(request):
    """Handle user login with email or phone number"""
    if request.method == 'POST':
        username = request.POST.get('username')  # Email or phone
        password = request.POST.get('password')

        logger.info(f"Login attempt with: {username}")

        user = None

        # Try to authenticate with email (most common)
        if '@' in username:
            user = authenticate(request, username=username, password=password)
            logger.info(f"Email authentication result: {user}")
        else:
            # If it's not an email, try to find user by phone number
            try:
                recipient = Recipient.objects.get(phone_number=username)
                user = authenticate(request, username=recipient.user.email, password=password)
                logger.info(f"Phone authentication result: {user}")
            except Recipient.DoesNotExist:
                logger.warning("No recipient found with this phone number")
                # Try direct username authentication as fallback
                user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"Login successful for user: {user}")

            # Check if user has a recipient profile
            if hasattr(user, 'recipient_profile'):
                messages.success(request, f'Welcome back, {user.recipient_profile.full_name}!')
                return redirect('/')
            else:
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect('/')
        else:
            logger.warning("Authentication failed")
            messages.error(request, 'Invalid email/phone or password')

    return render(request, 'login.html')


@login_required
def logout(request):
    """Logs out the user and shows the animated logout page"""
    auth_logout(request)
    return render(request, 'logout.html')


# ==================== DONOR REGISTRATION ====================

def register_donor(request):
    """Handle donor registration"""
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


# ==================== RECIPIENT REGISTRATION ====================

def register_recipient(request):
    """Handle recipient registration"""
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
                return redirect('login')
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


# ==================== DONOR DASHBOARD ====================

@login_required
def donor_dashboard(request):
    """Donor dashboard view - shows donor profile and stats"""
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found. Please complete your registration.")
        return redirect('donor_registration')

    # Calculate donation statistics
    total_donations = calculate_total_donations(donor)
    lives_saved = total_donations * 3  # Assuming each donation saves 3 lives

    # Get recent activities
    recent_activities = get_recent_activities(donor)

    context = {
        'donor': donor,
        'total_donations': total_donations,
        'lives_saved': lives_saved,
        'recent_activities': recent_activities,
    }

    return render(request, 'donors/donor_dashboard.html', context)


def calculate_total_donations(donor):
    """Calculate total number of donations based on donation history"""
    if not donor.last_donation_month or not donor.last_donation_year:
        return 0

    try:
        current_year = datetime.now().year
        last_donation_year = int(donor.last_donation_year)

        # Rough estimate based on eligibility (can donate every 3 months)
        years_since_first_donation = current_year - last_donation_year + 1
        estimated_donations = min(years_since_first_donation * 4, 20)

        return max(1, estimated_donations) if donor.last_donation_year else 0
    except (ValueError, TypeError):
        return 0


def get_recent_activities(donor):
    """Get recent activities for the donor"""
    activities = []

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

    return activities[:5]


@login_required
def donor_profile_update(request):
    """Handle donor profile updates"""
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    if request.method == 'POST':
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


# ==================== DONOR HISTORY ====================

@login_required
def donor_history(request):
    """Display donor's blood donation history"""
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
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
    lives_saved = total_donations * 3

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


# ==================== BLOOD REQUESTS ====================

@login_required
def blood_request_list(request):
    """Show blood requests that match donor's blood group"""
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    context = {
        'donor': donor,
        'requests': [],  # Replace with actual blood requests
    }

    return render(request, 'donors/blood_requests.html', context)


@login_required
def emergency_requests(request):
    """Show emergency blood requests"""
    try:
        donor = get_object_or_404(Donor, user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_registration')

    emergency_requests = []  # Replace with actual emergency requests

    context = {
        'donor': donor,
        'emergency_requests': emergency_requests,
    }

    return render(request, 'donors/emergency_requests.html', context)


# ==================== FIND BLOOD ====================

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

        # Add success message if donors found
        if donors.exists():
            messages.success(request, f'Found {donors.count()} available donor(s) in your area!')
        else:
            messages.warning(request, 'No donors found matching your criteria. Try searching in nearby areas.')

    # Auto-create recipient profile for social auth users
    if request.user.is_authenticated and not hasattr(request.user, 'recipient_profile'):
        try:
            recipient = Recipient.objects.create(
                user=request.user,
                first_name=request.user.first_name or 'User',
                last_name=request.user.last_name or '',
                email=request.user.email,
                phone_number='',
                blood_group='',
                house_holding_no='',
                road_block='',
                thana='',
                post_office='',
                district='Dhaka'
            )
            messages.info(request, 'Welcome! Your recipient profile has been created. You can update it later.')
        except Exception as e:
            logger.error(f"Error creating recipient profile: {str(e)}")

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


# ==================== MATCHING ====================

@login_required
def matching(request):
    """Matching page for donors to see blood requests and respond"""
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
        donor_responses__donor=donor
    ).order_by('-urgency_level', '-created_at')

    # Get recent matches
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
    """Handle donor response to blood request"""
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

            # Send notification to recipient
            send_donor_response_notification(blood_request.recipient, response)

            if response.response == 'accept':
                messages.success(
                    request,
                    "Thank you for accepting this blood donation request! "
                    "The recipient has been notified and will contact you soon."
                )
            else:
                messages.info(request, "Response recorded. Thank you for your time.")

            return redirect('matching')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DonorResponseForm()

    context = {
        'donor': donor,
        'blood_request': blood_request,
        'form': form,
    }

    return render(request, 'respond_to_request.html', context)


# ==================== BLOOD REQUEST FROM DONOR ====================
@login_required
def show_request_form(request, donor_id):
    """
    Load the blood request form for a specific donor via AJAX
    """
    donor = get_object_or_404(Donor, id=donor_id)

    # Get recipient info
    try:
        recipient = Recipient.objects.get(user=request.user)
    except Recipient.DoesNotExist:
        return render(request, 'error_message.html', {
            'error': 'Recipient profile not found. Please register as a recipient first.'
        })

    context = {
        'donor': donor,
        'recipient': recipient,
    }

    return render(request, 'request_blood_form.html', context)


@login_required
def request_blood_from_donor(request, donor_id):
    """
    Handle blood request submission
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        })

    donor = get_object_or_404(Donor, id=donor_id)

    try:
        recipient = Recipient.objects.get(user=request.user)
    except Recipient.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Recipient profile not found'
        })

    try:
        # Parse the needed_by_date
        needed_by_str = request.POST.get('needed_by_date')
        needed_by_date = timezone.datetime.fromisoformat(needed_by_str.replace('T', ' '))

        # Make it timezone-aware if needed
        if timezone.is_naive(needed_by_date):
            needed_by_date = timezone.make_aware(needed_by_date)

        # Calculate expiry (7 days from now or needed_by_date, whichever is earlier)
        expires_at = min(
            timezone.now() + timedelta(days=7),
            needed_by_date
        )

        # Create blood request
        blood_request = BloodRequest.objects.create(
            recipient=recipient,
            patient_name=request.POST.get('patient_name'),
            patient_age=int(request.POST.get('patient_age')),
            blood_group_needed=donor.blood_group,
            medical_condition=request.POST.get('medical_condition', ''),
            hospital_name=request.POST.get('hospital_name'),
            hospital_address=request.POST.get('hospital_address'),
            thana=donor.thana,
            district=donor.district,
            units_needed=int(request.POST.get('units_needed', 1)),
            urgency_level=request.POST.get('urgency_level', 'medium'),
            needed_by_date=needed_by_date,
            contact_person=request.POST.get('contact_person'),
            contact_number=request.POST.get('contact_number'),
            alternative_contact=request.POST.get('alternative_contact', ''),
            additional_notes=request.POST.get('additional_notes', ''),
            status='active',
            expires_at=expires_at
        )

        # Send email notification to donor
        email_sent = send_blood_request_email_to_donor(donor, blood_request, recipient)

        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Blood request sent successfully!' + (
                    ' Email notification sent to donor.' if email_sent else '')
            })
        else:
            # Regular form submission - render success page
            message = 'Your blood request has been sent successfully!' + (
                ' The donor will receive an email notification.' if email_sent else '')
            return render(request, 'blood_request_success.html', {'message': message})

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating blood request: {str(e)}")

        return JsonResponse({
            'success': False,
            'error': f'Failed to create blood request: {str(e)}'
        })
# ==================== REWARDS ====================

def rewards(request):
    """Rewards page showing points, badges, and withdrawal options"""
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

        # Calculate lives saved
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

        # Badge existence flags for template
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
            **badge_flags,
        })

    return render(request, 'rewards.html', context)


@login_required
def withdraw_points(request):
    """Handle point withdrawal requests (currently disabled)"""
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

        # Note: WithdrawalRequest model should be imported if it exists
        # Or this feature should be commented out if not implemented yet
        messages.info(
            request,
            f"Withdrawal request for {points_to_withdraw} RD Points has been submitted. "
            "SSL Commerce integration will be available soon."
        )

    return redirect('rewards')


# ==================== HELPER FUNCTIONS ====================

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


# ==================== PLACEHOLDER VIEWS ====================

def track_requests(request):
    """Track blood requests page"""
    return render(request, 'track-requests.html')