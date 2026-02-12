from flask import session
from app.utils import db_utils


def get_user_turnus_set():
    """Get the turnus set for current user (their session choice or database active set)."""
    active_set = db_utils.get_active_turnus_set()

    user_choice = session.get('user_selected_turnus_set')
    if user_choice:
        all_sets = db_utils.get_all_turnus_sets()
        user_set = next((ts for ts in all_sets if ts['id'] == user_choice), None)
        if user_set:
            return user_set
        else:
            session.pop('user_selected_turnus_set', None)

    return active_set
