import time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from app.forms import CalculationForm
from app.utils import db_utils
from app.routes.main import df_manager, turnus_data

shifts = Blueprint('shifts', __name__)

# @shifts.route('/')
# @login_required
# def home(): 
#     form = CalculationForm()

#     # Gets the values set by the user 
#     form.helgetimer.data = session.get('helgetimer', '0')
#     form.helgetimer_dagtid.data = session.get('helgetimer_dagtid', '0')
#     form.natt_helg.data = session.get('natt_helg', '0')
#     form.tidlig.data = session.get('tidlig', '0')
#     form.tidlig_poeng.data = session.get('tidlig_poeng', '0')
#     form.before_6.data = session.get('before_6', '0')
#     form.ettermiddager.data = session.get('ettermiddager', '0')
#     form.ettermiddager_poeng.data = session.get('ettermiddager_poeng', '0')
#     form.slutt_for_20.data = session.get('slutt_for_20', '0')
#     form.nights.data = session.get('nights', '0')
#     form.nights_pts.data = session.get('nights_pts', '0')

#     sort_btn_name = df_manager.sort_by_btn_txt
#     favorites = db_utils.get_favorite_lst(current_user.get_id())
    
#     time.sleep(1)
    
#     return render_template('sort_shifts.html', 
#                          table_data=df_manager.df.to_dict(orient='records'),
#                          form=form,
#                          sort_by_btn_name=sort_btn_name,
#                          page_name='Sorter Turnuser',
#                          favorites=favorites)

@shifts.route('/turnusliste')
def turnusliste():
    # Get favorites for current user
    from flask_login import current_user
    favoritt = db_utils.get_favorite_lst(current_user.get_id()) if current_user.is_authenticated else []
    
    return render_template('turnusliste.html', 
                         page_name='Turnusliste',
                         table_data=turnus_data,  # Add this
                         df=df_manager.df.to_dict(orient='records'),  # Add this
                         favoritt=favoritt)  # Add this



@shifts.route('/reset_search')
def reset_search():
    df_manager.df['poeng'] = 0

    session['helgetimer'] = 0
    session['helgetimer_dagtid'] = 0
    session['natt_helg'] = 0
    session['tidlig'] = 0
    session['tidlig_poeng'] = 0
    session['before_6'] = 0
    session['ettermiddager'] = 0
    session['ettermiddager_poeng'] = 0
    session['slutt_for_20'] = 0
    session['nights'] = 0
    session['nights_pts'] = 0
    
    df_manager.get_all_user_points()
    df_manager.sort_by('turnus', inizialize=True)

    return redirect(url_for('shifts.home'))

@shifts.route('/submit', methods=['POST'])
def calculate():
    form = CalculationForm()   
    if form.validate_on_submit():
        # Store form data in session
        session['helgetimer'] = form.helgetimer.data
        session['helgetimer_dagtid'] = form.helgetimer_dagtid.data
        session['natt_helg'] = form.natt_helg.data
        session['tidlig'] = form.tidlig.data
        session['tidlig_poeng'] = form.tidlig_poeng.data
        session['before_6'] = form.before_6.data
        session['ettermiddager'] = form.ettermiddager.data
        session['ettermiddager_poeng'] = form.ettermiddager_poeng.data
        session['slutt_for_20'] = form.slutt_for_20.data
        session['nights'] = form.nights.data
        session['nights_pts'] = form.nights_pts.data

        # Resets points value
        df_manager.df['poeng'] = 0
        df_manager.sort_by('turnus')

        helgetimer = float(form.helgetimer.data)
        df_manager.calc_multipliers('helgetimer', helgetimer)
        helgetimer_dagtid = float(form.helgetimer_dagtid.data)
        df_manager.calc_multipliers('helgetimer_dagtid', helgetimer_dagtid)
        
        natt_helg = float(form.natt_helg.data)
        df_manager.calc_multipliers('natt_helg', -natt_helg)

        tidlig = int(form.tidlig.data)
        tidlig_poeng = int(form.tidlig_poeng.data)
        df_manager.calc_thresholds('tidlig', tidlig, tidlig_poeng)

        before_6 = float(form.before_6.data)
        df_manager.calc_multipliers('before_6', before_6)

        # Calculate points for ettermiddager
        ettermiddager = int(form.ettermiddager.data)
        ettermiddager_pts = int(form.ettermiddager_poeng.data)
        df_manager.calc_thresholds('ettermiddag', ettermiddager, ettermiddager_pts)

        # Slutt før 20
        slutt_for_20 = int(form.slutt_for_20.data)
        df_manager.calc_multipliers('afternoon_ends_before_20', -slutt_for_20)

        # Calculate points for nights
        nights = int(form.nights.data)
        nights_pts = int(form.nights_pts.data)
        df_manager.calc_thresholds('natt', nights, nights_pts)
        
        df_manager.get_all_user_points()
        df_manager.sort_by('poeng')

        session.modified = True
        
        return redirect(url_for('shifts.home'))
    else:
        flash('Form validation failed. Please check your inputs.', 'danger')
        print("Form validation failed. Please check your inputs.")
        return redirect(url_for('shifts.home'))

@shifts.route('/sort_by_column')
def sort_by_column():
    column = request.args.get('column')
    if column in df_manager.df:
        df_manager.sort_by(column)
    else:
        df_manager.sort_by('poeng')

    return redirect(url_for('shifts.home'))

@shifts.route('/display_shift')
@login_required
def display_shift():
    shift_title = request.args.get('shift_title')
    if not shift_title:
        flash('No shift selected.', 'danger')
        return redirect(url_for('shifts.home'))
    
    # Find the shift data
    shift_data = None
    for shift_group in turnus_data:
        if shift_title in shift_group:
            shift_data = shift_group[shift_title]
            break
    
    if not shift_data:
        flash('Shift not found.', 'danger')
        return redirect(url_for('shifts.home'))
    
    # Get user rating for this shift - FIX THIS LINE
    user_rating = db_utils.get_shift_rating(current_user.get_id(), shift_title)  # Changed from get_user_rating
    
    return render_template('selected_shift.html',
                         shift_title=shift_title,
                         shift_data=shift_data,
                         user_rating=user_rating,
                         page_name=shift_title)

@shifts.route('/next_shift')
def next_shift():
    current_shift = request.args.get('current_shift')
    if not current_shift:
        return redirect(url_for('shifts.home'))
    
    # Find current shift index and get next one
    all_shifts = []
    for shift_group in turnus_data:
        all_shifts.extend(list(shift_group.keys()))
    
    try:
        current_index = all_shifts.index(current_shift)
        next_index = (current_index + 1) % len(all_shifts)
        next_shift = all_shifts[next_index]
        return redirect(url_for('shifts.display_shift', shift_title=next_shift))
    except ValueError:
        return redirect(url_for('shifts.turnusliste'))

@shifts.route('/favorites')
@login_required
def favorites():
    fav_order_lst = db_utils.get_favorite_lst(current_user.get_id())
    fav_dict_lookup = {}

    for x in turnus_data:
        for name, data in x.items():
            if name in fav_order_lst:
                fav_dict_lookup[name] = data
    fav_dict_sorted = [{name: fav_dict_lookup[name]} for name in fav_order_lst if name in fav_dict_lookup]

    return render_template('favorites.html',
                         page_name='Favoritter',
                         favorites=fav_dict_sorted,
                         df=df_manager.df.to_dict(orient='records'))

