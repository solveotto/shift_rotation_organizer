from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import logout_user, login_required, login_user as flask_login_user, current_user
from mysql.connector import Error
from app.forms import LoginForm
from app.models import User
from app.utils import db_utils

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # from app.routes.main import current_user  # Import here to avoid circular imports

    if current_user.is_authenticated:
        return redirect(url_for('shifts.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            db_user_data = db_utils.get_user_data(form.username.data)
            if db_user_data and User.verify_password(db_user_data['password'], form.password.data):
                # Check email verification status
                if db_user_data.get('email_verified') == 0:
                    flash('Please verify your email before logging in. Check your inbox for the verification link.', 'warning')
                    return render_template('login.html', form=form)

                user = User(form.username.data, db_user_data['id'], db_user_data['is_auth'])
                flask_login_user(user)

                # Clear any previous turnus set choice for fresh start
                session.pop('user_selected_turnus_set', None)

                return redirect(url_for('shifts.index'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        except Error as e:
            print(f'Error: {e}')
    else:
        print("ERROR", form.errors)
    
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    # Clear turnus set choice on logout
    session.pop('user_selected_turnus_set', None)
    logout_user()
    return render_template('logout.html') 