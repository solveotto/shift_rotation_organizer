import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.forms import CreateUserForm, EditUserForm, CreateTurnusSetForm, SelectTurnusSetForm, UploadStreklisteForm
from app.utils import db_utils
from app.utils import strekliste_generator

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
            email=form.email.data,
            rullenummer=form.rullenummer.data,
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
        form.email.data = user.get('email')
        form.rullenummer.data = user.get('rullenummer')
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
    upload_form = UploadStreklisteForm()

    return render_template('admin_turnus_sets.html',
                         page_name='Manage Turnus Sets',
                         turnus_sets=turnus_sets,
                         active_set=active_set,
                         upload_form=upload_form)

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

    # Get the turnus set info before deleting (for cleanup)
    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    version = turnus_set['year_identifier'].lower() if turnus_set else None

    success, message = db_utils.delete_turnus_set(turnus_set_id)

    if success:
        # Also delete strekliste images if they exist
        if version:
            img_result = strekliste_generator.delete_all_images(version)
            if img_result.get('deleted_count', 0) > 0:
                message += f" ({img_result['deleted_count']} strekliste images also deleted)"

        # If we deleted the active set, reload the data manager
        from app.routes.main import df_manager
        df_manager.reload_active_set()
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('admin.manage_turnus_sets'))

# Authorized Email Management Routes
@admin.route('/authorized-emails')
@login_required
def manage_authorized_emails():
    """Manage authorized emails for self-registration"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('shifts.home'))

    emails = db_utils.get_all_authorized_emails()
    return render_template('admin_authorized_emails.html',
                         page_name='Manage Authorized Emails',
                         emails=emails)

@admin.route('/add-authorized-email', methods=['POST'])
@login_required
def add_authorized_email():
    """Add new authorized email"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('shifts.home'))

    email = request.form.get('email', '').lower().strip()
    rullenummer = request.form.get('rullenummer', '').strip()
    notes = request.form.get('notes', '').strip()

    if not email:
        flash('Email address is required.', 'danger')
        return redirect(url_for('admin.manage_authorized_emails'))

    if not rullenummer:
        flash('Rullenummer is required.', 'danger')
        return redirect(url_for('admin.manage_authorized_emails'))

    success, message = db_utils.add_authorized_email(
        email=email,
        added_by=current_user.id,
        notes=notes,
        rullenummer=rullenummer
    )

    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.manage_authorized_emails'))

@admin.route('/delete-authorized-email/<int:email_id>', methods=['POST'])
@login_required
def delete_authorized_email(email_id):
    """Remove authorized email"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('shifts.home'))

    success, message = db_utils.delete_authorized_email(email_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.manage_authorized_emails'))

@admin.route('/bulk-add-emails', methods=['POST'])
@login_required
def bulk_add_authorized_emails():
    """Bulk add emails from textarea (one per line)"""
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('shifts.home'))

    emails_text = request.form.get('emails_bulk', '')
    emails = [e.strip().lower() for e in emails_text.split('\n') if e.strip()]

    added_count = 0
    for email in emails:
        success, _ = db_utils.add_authorized_email(
            email=email,
            added_by=current_user.id,
            notes='Bulk import'
        )
        if success:
            added_count += 1

    flash(f'Added {added_count} of {len(emails)} emails.', 'success')
    return redirect(url_for('admin.manage_authorized_emails'))


# Strekliste Management Routes
@admin.route('/strekliste-status/<int:turnus_set_id>')
@login_required
def strekliste_status(turnus_set_id):
    """AJAX endpoint to get strekliste status for a turnus set"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403

    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    if not turnus_set:
        return jsonify({'status': 'error', 'message': 'Turnus set not found'}), 404

    version = turnus_set['year_identifier'].lower()
    status = strekliste_generator.get_strekliste_status(version)

    return jsonify({
        'status': 'success',
        'data': status
    })


@admin.route('/upload-strekliste/<int:turnus_set_id>', methods=['POST'])
@login_required
def upload_strekliste(turnus_set_id):
    """Upload a strekliste PDF for a turnus set"""
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('admin.manage_turnus_sets'))

    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    if not turnus_set:
        flash('Turnus set not found.', 'danger')
        return redirect(url_for('admin.manage_turnus_sets'))

    form = UploadStreklisteForm()
    if form.validate_on_submit():
        pdf_file = form.pdf_file.data
        version = turnus_set['year_identifier'].lower()

        result = strekliste_generator.save_uploaded_pdf(pdf_file, version)

        if result['success']:
            flash(f'Strekliste PDF uploaded successfully for {turnus_set["year_identifier"]}.', 'success')
        else:
            flash(f'Failed to upload PDF: {result["error"]}', 'danger')
    else:
        flash('Invalid file. Please upload a PDF file.', 'danger')

    return redirect(url_for('admin.manage_turnus_sets'))


@admin.route('/generate-strekliste/<int:turnus_set_id>', methods=['POST'])
@login_required
def generate_strekliste(turnus_set_id):
    """Generate PNG images from strekliste PDF"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403

    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    if not turnus_set:
        return jsonify({'status': 'error', 'message': 'Turnus set not found'}), 404

    version = turnus_set['year_identifier'].lower()

    # Check if PDF exists
    paths = strekliste_generator.get_paths(version)
    if not paths['pdf_exists']:
        return jsonify({
            'status': 'error',
            'message': 'No strekliste PDF found. Please upload one first.'
        }), 400

    # Check if force regenerate is requested
    force = request.json.get('force', False) if request.is_json else False

    # Generate images
    result = strekliste_generator.generate_all_images(version, force=force)

    if result['success']:
        error_count = len(result.get('errors', []))
        message = f'Generated {len(result["generated"])} images'
        if error_count > 0:
            message += f' ({error_count} errors)'

        return jsonify({
            'status': 'success',
            'message': message,
            'generated': len(result['generated']),
            'skipped': len(result['skipped']),
            'errors': error_count,
            'error_details': result.get('errors', [])[:10],  # First 10 errors
            'total': result['total']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result.get('error', 'Unknown error')
        }), 500


@admin.route('/delete-strekliste-images/<int:turnus_set_id>', methods=['POST'])
@login_required
def delete_strekliste_images(turnus_set_id):
    """Delete all generated strekliste images for a turnus set"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403

    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    if not turnus_set:
        return jsonify({'status': 'error', 'message': 'Turnus set not found'}), 404

    version = turnus_set['year_identifier'].lower()
    result = strekliste_generator.delete_all_images(version)

    if result['success']:
        return jsonify({
            'status': 'success',
            'message': f'Deleted {result["deleted_count"]} images',
            'deleted_count': result['deleted_count']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result.get('error', 'Unknown error')
        }), 500