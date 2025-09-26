import time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from app.utils import db_utils, df_utils
from app.routes.main import df_manager, turnus_data

shifts = Blueprint('shifts', __name__)


@shifts.route('/')
@login_required
def turnusliste():
    # Get the turnus set for this user (their choice or system default)
    user_turnus_set = get_user_turnus_set()
    turnus_set_id = user_turnus_set['id'] if user_turnus_set else None
    
    # Get favorites for current user and active turnus set
    favoritt = db_utils.get_favorite_lst(current_user.get_id(), turnus_set_id) if current_user.is_authenticated else []
    
    # Load data for user's selected year
    user_df_manager = df_utils.DataframeManager(turnus_set_id)
    
    return render_template('turnusliste.html', 
                         page_name='Turnusliste',
                         table_data=user_df_manager.turnus_data,  
                         df=user_df_manager.df.to_dict(orient='records') if not user_df_manager.df.empty else [], 
                         favoritt=favoritt,
                         current_turnus_set=user_turnus_set,
                         all_turnus_sets=db_utils.get_all_turnus_sets())


@shifts.route('/switch-year/<int:turnus_set_id>')
@login_required
def switch_user_year(turnus_set_id):
    """Allow user to switch which year they're viewing (stored in session)"""
    print(f"DEBUG SWITCH: Switching to turnus_set_id = {turnus_set_id}")
    
    # Store user's choice in their session
    session['user_selected_turnus_set'] = turnus_set_id

    # Get the referring page (where user came from)
    next_page = request.args.get('next') or request.referrer
    
    # If no referrer or if it's the same switch route, default to turnusliste
    if not next_page or '/switch-year/' in next_page:
        next_page = url_for('shifts.turnusliste')
    
    flash(f'Switched to viewing turnus set', 'success')
    return redirect(next_page)

def get_user_turnus_set():
    """Get the turnus set for current user (their current session choice or database active set)"""
    # Get the current database active set
    active_set = db_utils.get_active_turnus_set()
    
    # Check if user has selected a specific year to view in THIS session
    user_choice = session.get('user_selected_turnus_set')
    if user_choice:
        from app.utils.db_utils import get_all_turnus_sets
        all_sets = get_all_turnus_sets()
        user_set = next((ts for ts in all_sets if ts['id'] == user_choice), None)
        if user_set:
            # If user's session choice exists, use it
            return user_set
        else:
            # If user's session choice doesn't exist anymore, clear it
            session.pop('user_selected_turnus_set', None)
    
    # Always default to the database active set
    return active_set


@shifts.route('/favorites')
@login_required
def favorites():
    # Get user's selected turnus set (same logic as turnusliste)
    user_turnus_set = get_user_turnus_set()
    turnus_set_id = user_turnus_set['id'] if user_turnus_set else None
    
    # Get favorites for the user's selected turnus set
    fav_order_lst = db_utils.get_favorite_lst(current_user.get_id(), turnus_set_id)
    
    # Load data for the user's selected turnus set
    user_df_manager = df_utils.DataframeManager(turnus_set_id)
    
    fav_dict_lookup = {}
    
    # Use the user's selected turnus data, not global data
    for x in user_df_manager.turnus_data:
        for name, data in x.items():
            if name in fav_order_lst:
                fav_dict_lookup[name] = data
    fav_dict_sorted = [{name: fav_dict_lookup[name]} for name in fav_order_lst if name in fav_dict_lookup]

    return render_template('favorites.html',
                        page_name='Favoritter',
                        favorites=fav_dict_sorted,
                        df=user_df_manager.df.to_dict(orient='records') if not user_df_manager.df.empty else [],
                        current_turnus_set=user_turnus_set,
                        all_turnus_sets=db_utils.get_all_turnus_sets()
                        )

@shifts.route('/compare')
@login_required
def compare():
    # Get user's selected turnus set
    user_turnus_set = get_user_turnus_set()
    turnus_set_id = user_turnus_set['id'] if user_turnus_set else None
    
    # Load data for user's selected year
    user_df_manager = df_utils.DataframeManager(turnus_set_id)
    
    # Prepare metrics for charts
    df = user_df_manager.df
    metrics = ['natt', 'tidlig', 'shift_cnt', 'before_6', 'helgetimer']
    labels = df['turnus'].tolist() if not df.empty else []
    data = {m: df[m].tolist() if m in df else [] for m in metrics}

    return render_template(
        'compare.html',
        page_name='Sammenlign Turnuser',
        labels=labels,
        data=data,
        current_turnus_set=user_turnus_set,
        all_turnus_sets=db_utils.get_all_turnus_sets()
    )

