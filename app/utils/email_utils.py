"""
Email utility functions for user verification
"""

from flask_mail import Message
from app import mail
from flask import url_for, render_template
from config import conf

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

        # Create message
        msg = Message(
            subject=subject,
            recipients=[email],
            body=text_body,
            html=html_body
        )

        # Send email
        mail.send(msg)

        # Update user's verification_sent_at timestamp
        from app.utils.db_utils import update_verification_sent_time
        update_verification_sent_time(email)

        return True
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

        msg = Message(
            subject=subject,
            recipients=[email],
            body=text_body,
            html=html_body
        )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
