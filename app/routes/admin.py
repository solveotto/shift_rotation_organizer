from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms import CreateUserForm, EditUserForm
from app.utils import db_utils

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def admin_dashboard():
    # Check if user is authorized (is_auth = 1)
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges to view this page.', 'danger')
        return redirect(url_for('shifts.home'))
    
    users = db_utils.get_all_users()
    return render_template('admin.html', 
                         users=users,
                         page_name='Admin Panel')

@admin.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    # Check if user is authorized (is_auth = 1)
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges to perform this action.', 'danger')
        return redirect(url_for('shifts.home'))
    
    form = CreateUserForm()
    if form.validate_on_submit():
        success, message = db_utils.create_user(
            username=form.username.data,
            password=form.password.data,
            is_auth=1 if form.is_auth.data else 0
        )
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash(message, 'danger')
    
    return render_template('create_user.html', 
                         form=form,
                         page_name='Create User')

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Check if user is authorized (is_auth = 1)
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges to perform this action.', 'danger')
        return redirect(url_for('shifts.home'))
    
    user = db_utils.get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    form = EditUserForm()
    
    if form.validate_on_submit():
        success, message = db_utils.update_user(
            user_id=user_id,
            username=form.username.data,
            password=form.password.data if form.password.data else None,
            is_auth=1 if form.is_auth.data else 0
        )
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash(message, 'danger')
    elif request.method == 'GET':
        form.username.data = user['username']
        form.is_auth.data = user['is_auth'] == 1
    
    return render_template('edit_user.html', 
                         form=form,
                         user=user,
                         page_name='Edit User')

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # Check if user is authorized (is_auth = 1)
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges to perform this action.', 'danger')
        return redirect(url_for('shifts.home'))
    
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    success, message = db_utils.delete_user(user_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/toggle_auth/<int:user_id>', methods=['POST'])
@login_required
def toggle_auth(user_id):
    # Check if user is authorized (is_auth = 1)
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges to perform this action.', 'danger')
        return redirect(url_for('shifts.home'))
    
    # Prevent admin from disabling their own auth
    if user_id == current_user.id:
        flash('You cannot disable your own authentication.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    success, message = db_utils.toggle_user_auth(user_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.admin_dashboard')) 