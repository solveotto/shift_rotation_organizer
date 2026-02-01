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
        subject = "Bekreft e-posten din - Turnushjelper"

        # HTML body
        html_body = render_template('emails/verification_email.html',
                                    verification_url=verification_url,
                                    email=email)

        # Plain text fallback
        text_body = f"""
Velkommen til Turnushjelper!

Vennligst bekreft e-postadressen din ved å klikke på lenken nedenfor:

{verification_url}

Denne lenken utløper om 48 timer.

Hvis du ikke opprettet denne kontoen, kan du ignorere denne e-posten.

---
Turnushjelper
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
        subject = "Velkommen til Turnushjelper!"

        html_body = render_template('emails/welcome_email.html', email=email)

        text_body = f"""
Velkommen til Turnushjelper!

E-posten din er nå verifisert. Du kan nå logge inn og begynne å administrere vaktpreferansene dine.

Logg inn på: {url_for('auth.login', _external=True)}

Hvis du har spørsmål, vennligst kontakt administratoren din.

---
Turnushjelper
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
        subject = "Tilbakestill passordet ditt - Turnushjelper"

        # HTML body
        html_body = render_template('emails/password_reset_email.html',
                                    reset_url=reset_url,
                                    email=email)

        # Plain text fallback
        text_body = f"""
Forespørsel om tilbakestilling av passord

Du har bedt om å tilbakestille passordet for din Turnushjelper-konto.

Klikk på lenken nedenfor for å tilbakestille passordet ditt:

{reset_url}

Denne lenken utløper om 1 time.

Hvis du ikke ba om tilbakestilling av passord, kan du ignorere denne e-posten. Passordet ditt forblir uendret.

---
Turnushjelper
        """

        return send_mailgun_email(email, subject, text_body, html_body)
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
