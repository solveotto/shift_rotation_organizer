import os
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
        year_id = form.year_identifier.data.upper()
        
        # Determine file paths
        if form.use_existing_files.data:
            # Use existing files from turnusfiler directory
            from config import conf
            turnusfiler_dir = os.path.join(conf.static_dir, 'turnusfiler', year_id.lower())
            turnus_json_path = os.path.join(turnusfiler_dir, f'turnuser_{year_id}.json')
            df_json_path = os.path.join(turnusfiler_dir, f'turnus_df_{year_id}.json')
            
            # Check if main turnus file exists
            if not os.path.exists(turnus_json_path):
                flash(f'Turnus JSON file not found: {turnus_json_path}', 'danger')
                return render_template('admin_create_turnus_set.html',
                                     page_name='Create Turnus Set',
                                     form=form)
        else:
            # Handle PDF upload
            if not form.pdf_file.data:
                flash('Please upload a PDF file or use existing files.', 'danger')
                return render_template('admin_create_turnus_set.html',
                                     page_name='Create Turnus Set',
                                     form=form)
            
            # PDF upload - scrape it
            turnus_json_path, df_json_path = handle_pdf_upload(form.pdf_file.data, year_id)
            if not turnus_json_path:
                return render_template('admin_create_turnus_set.html',
                                     page_name='Create Turnus Set',
                                     form=form)
        
        # Generate statistics if missing
        if not df_json_path or not os.path.exists(df_json_path):
            try:
                from app.utils.shift_stats import Turnus
                from config import conf
                stats = Turnus(turnus_json_path)
                df_json_path = os.path.join(conf.static_dir, 'turnusfiler', year_id.lower(), f'turnus_df_{year_id}.json')
                stats.stats_df.to_json(df_json_path)
                flash('Statistics JSON generated automatically.', 'info')
            except Exception as e:
                flash(f'Error generating statistics: {e}', 'danger')
                return render_template('admin_create_turnus_set.html',
                                     page_name='Create Turnus Set',
                                     form=form)
        
        # Create turnus set in database
        success, message = db_utils.create_turnus_set(
            name=form.name.data,
            year_identifier=year_id,
            is_active=form.is_active.data,
            turnus_file_path=turnus_json_path,
            df_file_path=df_json_path
        )
        
        if success:
            # Add shifts to database
            turnus_set = db_utils.get_turnus_set_by_year(year_id)
            if turnus_set:
                db_utils.add_shifts_to_turnus_set(turnus_json_path, turnus_set['id'])
                flash(f'Turnus set {year_id} created successfully!', 'success')
            else:
                flash('Turnus set created but shifts not added.', 'warning')
            return redirect(url_for('admin.manage_turnus_sets'))
        else:
            flash(message, 'danger')
    
    return render_template('admin_create_turnus_set.html',
                         page_name='Create Turnus Set',
                         form=form)

def handle_pdf_upload(pdf_file, year_id):
    """Handle PDF upload and scraping"""
    try:
        from config import conf
        from app.utils.shiftscraper import ShiftScraper
        
        # Create turnusfiler directory
        turnusfiler_dir = os.path.join(conf.static_dir, 'turnusfiler', year_id.lower())
        os.makedirs(turnusfiler_dir, exist_ok=True)
        
        # Save PDF file
        pdf_path = os.path.join(turnusfiler_dir, f'turnuser_{year_id}.pdf')
        pdf_file.save(pdf_path)
        
        # Scrape PDF
        scraper = ShiftScraper()
        scraper.scrape_pdf(pdf_path, year_id)
        
        # Generate JSON files
        turnus_json_path = scraper.create_json(year_id=year_id)
        excel_path = scraper.create_excel(year_id=year_id)
        
        flash(f'PDF scraped successfully! Created JSON and Excel files.', 'success')
        return turnus_json_path, None  # df_json_path will be generated later
        
    except Exception as e:
        flash(f'Error scraping PDF: {e}', 'danger')
        return None, None

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