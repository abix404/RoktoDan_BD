# roktodanbdweb/utils.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_donor_welcome_email(donor):
    """
    Send welcome email to newly registered donor
    """
    try:
        subject = 'Welcome to RoktoDan BD - Donor Registration Successful!'

        # Simple text email for now
        message = f"""
        Dear {donor.full_name},

        Welcome to RoktoDan BD! Your donor registration has been completed successfully.

        Your Details:
        - Name: {donor.full_name}
        - Blood Group: {donor.blood_group}
        - Location: {donor.thana}, Dhaka

        Thank you for joining our life-saving mission!

        Best regards,
        RoktoDan BD Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [donor.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to donor: {donor.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to donor {donor.email}: {str(e)}")
        return False


def send_recipient_welcome_email(recipient):
    """
    Send welcome email to newly registered recipient
    """
    try:
        subject = 'Welcome to RoktoDan BD - Recipient Registration Successful!'

        message = f"""
        Dear {recipient.full_name},

        Welcome to RoktoDan BD! Your recipient account has been created successfully.

        Your Details:
        - Name: {recipient.full_name}
        - Blood Group: {recipient.blood_group}
        - Location: {recipient.thana}, Dhaka

        You can now search for blood donors in your area.

        Best regards,
        RoktoDan BD Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient.user_email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to recipient: {recipient.user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to recipient {recipient.user_email}: {str(e)}")
        return False


def send_admin_notification(user_type, user_data):
    """
    Send notification to admin about new registration
    """
    try:
        subject = f'New {user_type.title()} Registration - RoktoDan BD'

        message = f"""
        A new {user_type} has registered on RoktoDan BD:

        Name: {user_data.get('name', 'N/A')}
        Email: {user_data.get('email', 'N/A')}
        Blood Group: {user_data.get('blood_group', 'N/A')}
        Location: {user_data.get('location', 'N/A')}
        Phone: {user_data.get('phone', 'N/A')}
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        logger.info(f"Admin notification sent for new {user_type}")
        return True

    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        return False


# Legacy function names for backward compatibility
def send_registration_email(user_type, user_data):
    """Legacy function - redirects to appropriate welcome email"""
    if user_type == 'donor':
        return send_donor_welcome_email(user_data)
    elif user_type == 'recipient':
        return send_recipient_welcome_email(user_data)
    return False