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


def send_registration_email(user_type, user_data):
    """
    Legacy function - redirects to appropriate welcome email
    """
    if user_type == 'donor':
        return send_donor_welcome_email(user_data)
    elif user_type == 'recipient':
        return send_recipient_welcome_email(user_data)
    return False


def send_blood_request_email_to_donor(donor, blood_request, recipient):
    """
    Send email notification to donor when recipient requests blood
    """
    try:
        subject = f'🩸 New Blood Request - {blood_request.blood_group_needed} Needed'

        # Determine urgency color
        urgency_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        urgency_color = urgency_colors.get(blood_request.urgency_level, '#ffc107')

        # Plain text version
        text_content = f"""
Dear {donor.full_name},

You have received a new blood donation request!

URGENCY LEVEL: {blood_request.get_urgency_level_display().upper()}

PATIENT INFORMATION:
- Name: {blood_request.patient_name}
- Age: {blood_request.patient_age} years
- Blood Group Needed: {blood_request.blood_group_needed}
- Units Needed: {blood_request.units_needed}
- Medical Condition: {blood_request.medical_condition or 'Not specified'}

HOSPITAL DETAILS:
- Hospital: {blood_request.hospital_name}
- Address: {blood_request.hospital_address}
- Location: {blood_request.thana}, {blood_request.district}

TIMELINE:
- Blood Needed By: {blood_request.needed_by_date.strftime('%B %d, %Y at %I:%M %p')}
- Request Expires: {blood_request.expires_at.strftime('%B %d, %Y at %I:%M %p')}

CONTACT INFORMATION:
- Contact Person: {blood_request.contact_person}
- Phone: {blood_request.contact_number}
{f'- Alternative Contact: {blood_request.alternative_contact}' if blood_request.alternative_contact else ''}

{f'ADDITIONAL NOTES: {blood_request.additional_notes}' if blood_request.additional_notes else ''}

REQUESTED BY:
- Name: {recipient.full_name}
- Email: {recipient.user_email}
- Phone: {recipient.phone_number}

If you are available to donate, please respond as soon as possible or contact the requester directly.

Thank you for being a life-saver!

Best regards,
RoktoDan BD Team
        """

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .urgency-badge {{
            display: inline-block;
            padding: 10px 20px;
            background-color: {urgency_color};
            color: white;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.2rem;
            margin: 15px 0;
            text-transform: uppercase;
        }}
        .info-box {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }}
        .info-label {{
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 10px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }}
        .contact-box {{
            background-color: #e7f3ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩸 New Blood Donation Request</h1>
            <p style="font-size: 1.5rem; margin: 10px 0;">Blood Group: <strong>{blood_request.blood_group_needed}</strong></p>
        </div>

        <div class="content">
            <p>Dear <strong>{donor.full_name}</strong>,</p>

            <p>You have received a new blood donation request that matches your blood group and location!</p>

            <center>
                <div class="urgency-badge">{blood_request.get_urgency_level_display()}</div>
            </center>

            <div class="info-box">
                <p class="info-label">PATIENT INFORMATION</p>
                <p><strong>Name:</strong> {blood_request.patient_name}</p>
                <p><strong>Age:</strong> {blood_request.patient_age} years</p>
                <p><strong>Blood Group Needed:</strong> <span style="color: #dc3545; font-weight: bold;">{blood_request.blood_group_needed}</span></p>
                <p><strong>Units Needed:</strong> {blood_request.units_needed}</p>
                {f'<p><strong>Medical Condition:</strong> {blood_request.medical_condition}</p>' if blood_request.medical_condition else ''}
            </div>

            <div class="info-box">
                <p class="info-label">HOSPITAL DETAILS</p>
                <p><strong>Hospital:</strong> {blood_request.hospital_name}</p>
                <p><strong>Address:</strong> {blood_request.hospital_address}</p>
                <p><strong>Location:</strong> {blood_request.thana}, {blood_request.district}</p>
            </div>

            <div class="highlight">
                <p style="margin: 0;"><strong>⏰ Blood Needed By:</strong></p>
                <p style="font-size: 1.2rem; color: #dc3545; font-weight: bold; margin: 5px 0;">
                    {blood_request.needed_by_date.strftime('%B %d, %Y at %I:%M %p')}
                </p>
                <p style="margin: 0; font-size: 0.9rem; color: #666;">
                    Request expires: {blood_request.expires_at.strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>

            <div class="contact-box">
                <h3>Contact Information</h3>
                <p><strong>Contact Person:</strong> {blood_request.contact_person}</p>
                <p style="font-size: 1.3rem; font-weight: bold; color: #dc3545;">
                    📞 {blood_request.contact_number}
                </p>
                {f'<p><strong>Alternative Contact:</strong> {blood_request.alternative_contact}</p>' if blood_request.alternative_contact else ''}
            </div>

            {f'<div class="info-box"><p class="info-label">ADDITIONAL NOTES</p><p>{blood_request.additional_notes}</p></div>' if blood_request.additional_notes else ''}

            <div class="info-box">
                <p class="info-label">REQUESTED BY</p>
                <p><strong>Name:</strong> {recipient.full_name}</p>
                <p><strong>Email:</strong> {recipient.user_email}</p>
                <p><strong>Phone:</strong> {recipient.phone_number}</p>
            </div>

            <center>
                <p style="margin: 20px 0; font-size: 1.1rem;">
                    <strong>Can you help save a life?</strong>
                </p>
                <p>If you are available to donate, please contact the requester directly at the number above.</p>
            </center>
        </div>

        <div class="footer">
            <p><strong>RoktoDan BD</strong></p>
            <p>Thank you for being a life-saver!</p>
            <p style="font-size: 0.9rem; color: #999;">
                This is an automated notification. Please do not reply to this email.
            </p>
        </div>
    </div>
</body>
</html>
        """

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[donor.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Blood request notification sent to donor: {donor.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send blood request email to donor: {str(e)}")
        return False


def send_donor_response_notification(recipient, donor_response):
    """
    Notify recipient when donor responds to their blood request
    """
    try:
        donor = donor_response.donor
        blood_request = donor_response.blood_request
        response_type = donor_response.get_response_display()

        if donor_response.response == 'accept':
            subject = f'✅ Donor Accepted Your Blood Request - {blood_request.blood_group_needed}'
            status_color = '#28a745'
            status_message = 'ACCEPTED'
        else:
            subject = f'Blood Request Response - {blood_request.blood_group_needed}'
            status_color = '#dc3545'
            status_message = 'DECLINED'

        # Plain text version
        text_content = f"""
Dear {recipient.full_name},

A donor has responded to your blood request!

DONOR RESPONSE: {response_type.upper()}

DONOR DETAILS:
- Name: {donor.full_name}
- Blood Group: {donor.blood_group}
- Location: {donor.thana}, {donor.district}
- Phone: {donor.phone_number}
- Email: {donor.email}

REQUEST DETAILS:
- Patient: {blood_request.patient_name}
- Hospital: {blood_request.hospital_name}
- Needed By: {blood_request.needed_by_date.strftime('%B %d, %Y at %I:%M %p')}

{f'DONOR NOTES: {donor_response.notes}' if donor_response.notes else ''}

{f'PREFERRED DONATION TIME: {donor_response.preferred_donation_time.strftime("%B %d, %Y at %I:%M %p")}' if donor_response.preferred_donation_time else ''}

{f'AVAILABILITY NOTES: {donor_response.availability_notes}' if donor_response.availability_notes else ''}

{f"Please contact the donor at {donor.phone_number} to coordinate the donation." if donor_response.response == 'accept' else "You may want to search for other available donors in your area."}

Thank you for using RoktoDan BD!

Best regards,
RoktoDan BD Team
        """

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 10px 20px;
            background-color: {status_color};
            color: white;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.2rem;
            margin: 15px 0;
        }}
        .info-box {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid {status_color};
            border-radius: 4px;
        }}
        .info-label {{
            font-weight: bold;
            color: {status_color};
        }}
        .contact-box {{
            background-color: #e7f3ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{'✅' if donor_response.response == 'accept' else '📋'} Donor Response</h1>
        </div>

        <div class="content">
            <p>Dear <strong>{recipient.full_name}</strong>,</p>

            <p>A donor has responded to your blood request!</p>

            <center>
                <div class="status-badge">{status_message}</div>
            </center>

            <div class="info-box">
                <p class="info-label">DONOR INFORMATION</p>
                <p><strong>Name:</strong> {donor.full_name}</p>
                <p><strong>Blood Group:</strong> {donor.blood_group}</p>
                <p><strong>Location:</strong> {donor.thana}, {donor.district}</p>
                <p><strong>Phone:</strong> {donor.phone_number}</p>
                <p><strong>Email:</strong> {donor.email}</p>
            </div>

            <div class="info-box">
                <p class="info-label">YOUR REQUEST DETAILS</p>
                <p><strong>Patient:</strong> {blood_request.patient_name}</p>
                <p><strong>Hospital:</strong> {blood_request.hospital_name}</p>
                <p><strong>Needed By:</strong> {blood_request.needed_by_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            f'<div class="info-box"><p class="info-label">DONOR\'S NOTES</p><p>{donor_response.notes}</p></div>' if donor_response.notes else ''

            {f'<div class="info-box"><p class="info-label">PREFERRED DONATION TIME</p><p>{donor_response.preferred_donation_time.strftime("%B %d, %Y at %I:%M %p")}</p></div>' if donor_response.preferred_donation_time else ''}

            {f'<div class="info-box"><p class="info-label">AVAILABILITY</p><p>{donor_response.availability_notes}</p></div>' if donor_response.availability_notes else ''}

            {'<div class="contact-box"><h3>Next Steps</h3><p>Please contact the donor directly to coordinate the donation:</p><p style="font-size: 1.3rem; font-weight: bold; color: #dc3545;">📞 ' + donor.phone_number + '</p><p>Thank you for using RoktoDan BD to find a donor!</p></div>' if donor_response.response == 'accept' else '<div class="contact-box"><p>The donor is unable to donate at this time. Please continue searching for other available donors in your area.</p></div>'}
        </div>

        <div class="footer">
            <p><strong>RoktoDan BD</strong></p>
            <p>Connecting donors with those in need</p>
        </div>
    </div>
</body>
</html>
        """

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.user_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Donor response notification sent to {recipient.user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send donor response notification: {str(e)}")
        return False