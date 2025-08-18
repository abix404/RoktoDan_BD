from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_registration_email(recipient):
    """Send registration confirmation email to recipient"""
    try:
        subject = 'Welcome to RoktoDan BD - Recipient Registration Confirmed'

        # Create HTML email content
        html_content = render_to_string('emails/recipient_registration.html', {
            'recipient': recipient,
            'site_name': 'RoktoDan BD'
        })

        # Create plain text version
        text_content = strip_tags(html_content)

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email]
        )
        msg.attach_alternative(html_content, "text/html")

        # Send email
        msg.send()

        logger.info(f"Registration email sent successfully to {recipient.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send registration email to {recipient.email}: {str(e)}")
        return False


def send_simple_registration_email(recipient):
    """Simple text-based registration email"""
    try:
        subject = 'Welcome to RoktoDan BD - Recipient Registration Confirmed'
        message = f"""
Dear {recipient.full_name},

Thank you for registering as a blood recipient with RoktoDan BD!

Your Registration Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Name: {recipient.full_name}
- Required Blood Group: {recipient.blood_group}
- Phone Number: {recipient.phone_number}
- Email: {recipient.email}
- Location: {recipient.full_address}
{f'• Age: {recipient.age}' if recipient.age else ''}

What's Next?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Your registration is now active
✓ We will search for compatible donors in your area
✓ You'll receive notifications when donors are available
✓ Keep your phone accessible for urgent blood requests

Important Notes:
- Ensure your contact information is always up to date
- Response time is crucial in emergency situations
- You can update your information anytime through our platform

Need Help?
If you have any questions or need to update your information, please contact us.

Best regards,
RoktoDan BD Team
Supporting Life, One Drop at a Time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )

        logger.info(f"Simple registration email sent to {recipient.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
        return False


def send_admin_notification(recipient):
    """Send notification to admin about new recipient registration"""
    try:
        subject = f'New Recipient Registration - {recipient.blood_group} Blood Type'
        message = f"""
New recipient has registered on RoktoDan BD:

Name: {recipient.full_name}
Blood Group: {recipient.blood_group}
Phone: {recipient.phone_number}
Email: {recipient.email}
Location: {recipient.full_address}
Registration Time: {recipient.created_at}

Please review and activate the account if necessary.
        """

        admin_emails = ['admin@roktodan.bd']  # Add admin emails here

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=True,
        )

        return True
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        return False