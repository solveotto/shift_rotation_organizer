"""
Email utility functions for user verification
"""

import os
import requests
from flask import url_for, render_template
from config import conf


def send_mailgun_email(to_email, subject, text_body, html_body):
    """Send email using Mailgun API"""
    try:
        # Get Mailgun configuration
        mailgun_api_key = conf.CONFIG.get('email', 'mailgun_api_key', fallback=os.getenv('MAILGUN_API_KEY'))
        mailgun_domain = conf.CONFIG.get('email', 'mailgun_domain', fallback='mail.turnushjelper.no')
        mailgun_region = conf.CONFIG.get('email', 'mailgun_region', fallback='eu')
        sender_name = conf.CONFIG.get('email', 'sender_name')
        sender_email = conf.CONFIG.get('email', 'sender_email')

        # Build API URL based on region
        if mailgun_region == 'eu':
            api_url = f"https://api.eu.mailgun.net/v3/{mailgun_domain}/messages"
        else:
            api_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"

        # Prepare email data
        data = {
            "from": f"{sender_name} <{sender_email}>",
            "to": to_email,
            "subject": subject,
            "text": text_body,
            "html": html_body
        }

        # Send request to Mailgun API
        response = requests.post(
            api_url,
            auth=("api", mailgun_api_key),
            data=data,
            timeout=10
        )

        # Check response
        if response.status_code == 200:
            return True
        else:
            print(f"Mailgun API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error sending email via Mailgun API: {e}")
        return False


def send_verification_email(email, token):
    """Send verification email to user"""
    try:
        # Build verification URL
        verification_url = url_for('registration.verify_email',
                                   token=token,
                                   _external=True)

        # Email subject
        subject = "Verify Your Email - Shift Rotation System"

        # HTML body
        html_body = render_template('emails/verification_email.html',
                                    verification_url=verification_url,
                                    email=email)

        # Plain text fallback
        text_body = f"""
Welcome to Shift Rotation System!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 48 hours.

If you did not create this account, please ignore this email.

---
Shift Rotation System
        """

        # Send email via Mailgun API
        success = send_mailgun_email(email, subject, text_body, html_body)

        if success:
            # Update user's verification_sent_at timestamp
            from app.utils.db_utils import update_verification_sent_time
            update_verification_sent_time(email)

        return success
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_welcome_email(email):
    """Send welcome email after successful verification"""
    try:
        subject = "Welcome to Shift Rotation System!"

        html_body = render_template('emails/welcome_email.html', email=email)

        text_body = f"""
Welcome to Shift Rotation System!

Your email has been verified successfully. You can now log in and start managing your shift preferences.

Log in at: {url_for('auth.login', _external=True)}

If you have any questions, please contact your administrator.

---
Shift Rotation System
        """

        return send_mailgun_email(email, subject, text_body, html_body)
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_password_reset_email(email, token):
    """Send password reset email to user"""
    try:
        # Build reset URL
        reset_url = url_for('auth.reset_password',
                            token=token,
                            _external=True)

        # Email subject
        subject = "Reset Your Password - Shift Rotation System"

        # HTML body
        html_body = render_template('emails/password_reset_email.html',
                                    reset_url=reset_url,
                                    email=email)

        # Plain text fallback
        text_body = f"""
Password Reset Request

You have requested to reset your password for your Shift Rotation System account.

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email. Your password will remain unchanged.

---
Shift Rotation System
        """

        return send_mailgun_email(email, subject, text_body, html_body)
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
