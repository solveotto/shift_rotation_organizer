from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import logout_user, login_required, login_user as flask_login_user
from mysql.connector import Error
from app.forms import LoginForm
from app.models import User
from app.utils import db_utils

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    from app.routes.main import current_user  # Import here to avoid circular imports
    
    if current_user.is_authenticated:
        return redirect(url_for('shifts.home'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            db_user_data = db_utils.get_user_data(form.username.data)
            if db_user_data and User.verify_password(db_user_data['password'], form.password.data):
                user = User(form.username.data, db_user_data['id'], db_user_data['is_auth'])
                flask_login_user(user)
                return redirect(url_for('shifts.home'))
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
    logout_user()
    return redirect(url_for('auth.login')) 