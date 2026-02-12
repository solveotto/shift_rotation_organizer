from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user, login_required


def admin_required(f):
    """Decorator that requires the user to be logged in AND an admin.

    For JSON/AJAX requests: returns 403 JSON response.
    For normal requests: flashes a message and redirects.
    Includes @login_required so routes don't need both decorators.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': 'Access denied'}), 403
            flash('Ingen tilgang. Administratorrettigheter påkrevd.', 'danger')
            return redirect(url_for('shifts.index'))
        return f(*args, **kwargs)
    return decorated_function
