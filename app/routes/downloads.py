import os
import logging
from flask import Blueprint, send_from_directory, flash, redirect, url_for
from flask_login import login_required
from config import AppConfig
from app.utils.turnus_helpers import get_user_turnus_set

logger = logging.getLogger(__name__)

downloads = Blueprint('downloads', __name__)


# Legacy route
@downloads.route('/download_excel')
@login_required
def download_excel():
    # Get user's selected turnus set (same logic as other routes)
    turnus_set = get_user_turnus_set()
    if not turnus_set:
        flash('No turnus set found', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    # Construct file path based on turnus set
    year_id = turnus_set['year_identifier'].lower()
    filename = f'turnuser_{turnus_set["year_identifier"]}.xlsx'
    directory = os.path.join(AppConfig.turnusfiler_dir, year_id)
    file_path = os.path.join(directory, filename)
    
    logger.debug("Download excel: directory=%s, filename=%s, path=%s", directory, filename, file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'Excel file not found for {turnus_set["year_identifier"]}. The file may not have been generated yet.', 'warning')
        return redirect(url_for('shifts.turnusliste'))
    
    return send_from_directory(directory, filename, as_attachment=True)

@downloads.route('/download_pdf')
@login_required
def download_pdf():
    # Get user's selected turnus set (same logic as other routes)
    turnus_set = get_user_turnus_set()
    if not turnus_set:
        flash('No turnus set found', 'danger')
        return redirect(url_for('shifts.turnusliste'))
    
    # Construct file path based on turnus set
    year_id = turnus_set['year_identifier'].lower()
    filename = f'turnuser_{turnus_set["year_identifier"]}.pdf'
    directory = os.path.join(AppConfig.turnusfiler_dir, year_id)
    file_path = os.path.join(directory, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'Turnus keys ZIP file not found for {turnus_set["year_identifier"]}. The file may not have been generated yet.', 'warning')
        return redirect(url_for('shifts.turnusliste'))
    
    return send_from_directory(directory, filename, as_attachment=True) 