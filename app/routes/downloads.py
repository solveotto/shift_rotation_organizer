import os
from flask import Blueprint, send_from_directory, request, session, flash, redirect, url_for
from config import conf
from app.utils import db_utils

downloads = Blueprint('downloads', __name__)

def get_user_turnus_set():
    """Get the turnus set for current user (their current session choice or database active set)"""
    # Get the current database active set
    active_set = db_utils.get_active_turnus_set()
    
    # Check if user has selected a specific year to view in THIS session
    user_choice = session.get('user_selected_turnus_set')
    if user_choice:
        all_sets = db_utils.get_all_turnus_sets()
        user_set = next((ts for ts in all_sets if ts['id'] == user_choice), None)
        if user_set:
            # If user's session choice exists, use it
            return user_set
        else:
            # If user's session choice doesn't exist anymore, clear it
            session.pop('user_selected_turnus_set', None)
    
    # Always default to the database active set
    return active_set

@downloads.route('/download_excel')
def download_excel():
    # Get user's selected turnus set (same logic as other routes)
    turnus_set = get_user_turnus_set()
    if not turnus_set:
        flash('No turnus set found', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    # Construct file path based on turnus set
    year_id = turnus_set['year_identifier'].lower()
    filename = f'turnuser_{turnus_set["year_identifier"]}.xlsx'
    directory = os.path.join(conf.turnusfiler_dir, year_id)
    file_path = os.path.join(directory, filename)
    
    print(f"Directory: {directory}")
    print(f"Filename: {filename}")
    print(f"Full path: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'Excel file not found for {turnus_set["year_identifier"]}. The file may not have been generated yet.', 'warning')
        return redirect(url_for('shifts.turnusliste'))
    
    return send_from_directory(directory, filename, as_attachment=True)

@downloads.route('/download_turnusnokler_zip')
def download_turnusnokler_zip():
    # Get user's selected turnus set (same logic as other routes)
    turnus_set = get_user_turnus_set()
    if not turnus_set:
        flash('No turnus set found', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    # Construct file path based on turnus set
    year_id = turnus_set['year_identifier'].lower()
    filename = f'turnusnøkler_{turnus_set["year_identifier"]}.zip'
    directory = os.path.join(conf.turnusfiler_dir, year_id)
    file_path = os.path.join(directory, filename)
        
    print(f"Directory: {directory}")
    print(f"Filename: {filename}")
    print(f"Full path: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'Turnus keys ZIP file not found for {turnus_set["year_identifier"]}. The file may not have been generated yet.', 'warning')
        return redirect(url_for('shifts.turnusliste'))
    
    return send_from_directory(directory, filename, as_attachment=True) 