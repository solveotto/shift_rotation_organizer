from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms import RegisterForm, ResendVerificationForm
from app.utils import db_utils, email_utils
import secrets

registration = Blueprint('registration', __name__)

@registration.route('/register', methods=['GET', 'POST'])
def register():
    """Self-registration for users with authorized emails"""
    if current_user.is_authenticated:
        return redirect(url_for('shifts.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        username = form.username.data.strip()
        rullenummer = form.rullenummer.data.strip()

        # Check if email and rullenummer combination is authorized
        if not db_utils.is_email_authorized(email, rullenummer):
            flash('This email and work ID combination is not authorized. Contact an administrator.', 'danger')
            return render_template('register.html', form=form)

        # Check if email already registered
        if db_utils.get_user_by_email(email):
            flash('An account with this email already exists.', 'warning')
            return redirect(url_for('auth.login'))

        # Check if username already taken
        if db_utils.get_user_by_username(username):
            flash('This username is already taken. Please choose another.', 'warning')
            return render_template('register.html', form=form)

        # Create user account (unverified)
        success, message, user_id = db_utils.create_user_with_email(
            email=email,
            username=username,
            password=form.password.data,
            verified=False,
            rullenummer=rullenummer
        )

        if success:
            # Generate and send verification token
            token = secrets.token_urlsafe(32)
            db_utils.create_verification_token(user_id, token)
            email_utils.send_verification_email(email, token)

            flash('Registration successful! Check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')

    return render_template('register.html', form=form)

@registration.route('/verify/<token>')
def verify_email(token):
    """Verify email with token from email link"""
    result = db_utils.verify_token(token)

    if result['success']:
        # Send welcome email
        if 'email' in result:
            email_utils.send_welcome_email(result['email'])

        flash('Email verified successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(result['message'], 'danger')
        return redirect(url_for('registration.register'))

@registration.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email for unverified users"""
    form = ResendVerificationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = db_utils.get_user_by_email(email)

        if user and not user['email_verified']:
            # Rate limiting check
            if db_utils.can_send_verification_email(user['id']):
                token = secrets.token_urlsafe(32)
                db_utils.create_verification_token(user['id'], token)
                email_utils.send_verification_email(email, token)
                flash('Verification email resent. Check your inbox.', 'success')
            else:
                flash('Too many verification emails sent. Please try again later.', 'warning')
        else:
            flash('Email not found or already verified.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('resend_verification.html', form=form)
