from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms import CreateUserForm, EditUserForm, CreateTurnusSetForm, SelectTurnusSetForm
from app.utils import db_utils

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
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






    
@admin.route('/turnus-sets')
@login_required
def manage_turnus_sets():
    """Manage turnus sets"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    turnus_sets = db_utils.get_all_turnus_sets()
    active_set = db_utils.get_active_turnus_set()
    
    return render_template('admin_turnus_sets.html',
                         page_name='Manage Turnus Sets',
                         turnus_sets=turnus_sets,
                         active_set=active_set)

@admin.route('/create-turnus-set', methods=['GET', 'POST'])
@login_required
def create_turnus_set():
    """Create a new turnus set"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    form = CreateTurnusSetForm()
    
    if form.validate_on_submit():
        success, message = db_utils.create_turnus_set(
            name=form.name.data,
            year_identifier=form.year_identifier.data.upper(),
            is_active=form.is_active.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.manage_turnus_sets'))
        else:
            flash(message, 'danger')
    
    return render_template('admin_create_turnus_set.html',
                         page_name='Create Turnus Set',
                         form=form)

@admin.route('/switch-turnus-set', methods=['POST'])
@login_required
def switch_turnus_set():
    """Switch to a different turnus set"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    turnus_set_id = request.form.get('turnus_set_id', type=int)
    success, message = db_utils.set_active_turnus_set(turnus_set_id)
    
    if success:
        # Reload the data manager with new active set
        from app.routes.main import df_manager
        df_manager.reload_active_set()
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.manage_turnus_sets'))

@admin.route('/delete-turnus-set/<int:turnus_set_id>', methods=['POST'])
@login_required
def delete_turnus_set(turnus_set_id):
    """Delete a turnus set"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    success, message = db_utils.delete_turnus_set(turnus_set_id)
    
    if success:
        # If we deleted the active set, reload the data manager
        from app.routes.main import df_manager
        df_manager.reload_active_set()
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.manage_turnus_sets'))