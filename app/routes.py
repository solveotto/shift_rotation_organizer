import os
import time
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_login import login_user as flask_login_user
from mysql.connector import Error
from config import conf
from app.utils import df_utils, db_utils
from app.forms import LoginForm
from app.models import User

main = Blueprint('main', __name__)

with open(os.path.join(conf.static_dir, 'turnuser_R24.json'), 'r') as f:
            turnus_data = json.load(f)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            db_user_data = db_utils.get_user_data(form.username.data)
            if db_user_data and User.verify_password(db_user_data['password'], form.password.data):
                user = User(db_user_data['id'], form.username.data, db_user_data['is_auth'])
                flask_login_user(user)
                print('Flask Login')
                return redirect(url_for('main.home'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        except Error as e:
            print(f'Error: {e}')

    else:
        print("ERROR", form.errors)
    return render_template('login.html', 
                           form=form,
                            )

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

 
@main.route('/')
@login_required
def home(): 
    # Gets the values set by the user 
    helgetimer = session.get('helgetimer', '0')
    helgetimer_dagtid = session.get('helgetimer_dagtid', '0')
    natt_helg = session.get('natt_helg', '0')
    tidlig = session.get('tidlig', '0')
    tidlig_poeng = session.get('tidlig_poeng', '0')
    before_6 = session.get('before_6', '0')
    ettermiddager = session.get('ettermiddager', '0')
    ettermiddager_poeng = session.get('ettermiddager_poeng', '0')
    slutt_for_20 = session.get('slutt_for_20')
    nights = session.get('nights', '0')
    nights_pts = session.get('nights_pts', '0')


    sort_btn_name = df_manager.sort_by_btn_txt
    favorites = db_utils.get_favorite_lst(current_user.get_id())

     # Pass the table data to the template
    return render_template('sort_shifts.html', 
                           table_data = df_manager.df.to_dict(orient='records'), 
                           helgetimer = helgetimer,
                           helgetimer_dagtid = helgetimer_dagtid,
                           natt_helg = natt_helg,
                           tidlig = tidlig,
                           tidlig_poeng = tidlig_poeng,
                           before_6 = before_6,
                           ettermiddager = ettermiddager,
                           ettermiddager_poeng = ettermiddager_poeng,
                           slutt_for_20 = slutt_for_20,
                           nights = nights,
                           nights_pts = nights_pts,
                           sort_by_btn_name = sort_btn_name,
                           page_name = 'Filtrer Turnuser',
                           favorites = favorites
                           )


@main.route('/reset_search')
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

    return redirect(url_for('main.home'))


@main.route('/submit', methods=['POST'])
def calculate():
    # Resets points value
    df_manager.df['poeng'] = 0
    df_manager.sort_by('turnus')

    helgetimer = request.form.get('helgetimer', '0')
    df_manager.calc_multipliers('helgetimer', float(helgetimer))
    session['helgetimer'] = helgetimer
    
    helgetimer_dagtid = request.form.get('helgetimer_dagtid', '0')
    df_manager.calc_multipliers('helgetimer_dagtid', float(helgetimer_dagtid))
    session['helgetimer_dagtid'] = helgetimer_dagtid
    
    natt_helg = request.form.get('natt_helg', '0')
    session['natt_helg'] = natt_helg
    df_manager.calc_multipliers('natt_helg', -float(natt_helg))

    tidlig = request.form.get('tidlig', '0')
    tidlig_poeng = request.form.get('tidlig_poeng', '0')
    session['tidlig']= tidlig
    session['tidlig_poeng'] = tidlig_poeng
    df_manager.calc_thresholds('tidlig', int(tidlig), int(tidlig_poeng))

    before_6 = request.form.get('before_6', '0')
    session['before_6'] = before_6
    df_manager.calc_multipliers('before_6', int(before_6))

    # calculate points for ettermiddager
    ettermiddager = request.form.get('ettermiddager', '0')
    ettermiddager_pts = request.form.get('ettermiddager_poeng', '0')
    session['ettermiddager'] = ettermiddager
    session['ettermiddager_poeng'] = ettermiddager_pts
    df_manager.calc_thresholds('ettermiddag', int(ettermiddager), int(ettermiddager_pts))

    # Slutt før 20
    slutt_for_20 = request.form.get('slutt_for_20', '0')
    session['slutt_for_20'] = slutt_for_20
    df_manager.calc_multipliers('afternoon_ends_before_20', -int(slutt_for_20))

    # caluclate points for nights
    nights = request.form.get('nights', '0')
    nights_pts = request.form.get('nights_pts', '0')
    session['nights'] = nights
    session['nights_pts'] = nights_pts
    df_manager.calc_thresholds('natt', int(nights), int(nights_pts))

    df_manager.get_all_user_points()
    df_manager.sort_by('poeng')
    
    return redirect(url_for('main.home'))


@main.route('/sort_by_column')
def sort_by_column():
    column = request.args.get('column')
    if column in df_manager.df:
        df_manager.sort_by(column)
    else:
        df_manager.sort_by('poeng')

    return redirect(url_for('main.home'))



# This function is used by a javascript to make every line clickeable in the sorting view
@main.route('/api/select_shift', methods=['POST'])
def select_shift():
    html_data = request.get_json()
    selected_shift = html_data.get('turnus')
    session['selected_shift'] = selected_shift
    return redirect(url_for('main.display_shift'))


@main.route('/display_shift')
@login_required
def display_shift():
    ettermiddager = session.get('ettermiddager')
    selected_shift = session.get('selected_shift')
    selected_shift_df = df_manager.df[df_manager.df['turnus'] == selected_shift]

    for x in turnus_data:
        for title, data in x.items():
            if title == selected_shift:
                shift_title = title
                shift_data = data
   
    shift_user_points = db_ctrl.get_shift_rating(df_manager.user_id, shift_title)
    session['current_user_point_input'] = shift_user_points
    session['shift_title'] = shift_title
    
    # Denne listen burde kanskje lagres lokalt
    favorites_lst = db_utils.get_favorite_lst(current_user.get_id())

    if shift_title in favorites_lst:
        favoritt = 'checked'
    else:
        favoritt = ''

    if shift_title and shift_data:
        return render_template('selected_shift.html',
                               table_data = selected_shift_df.to_dict(orient='records'), 
                               shift_title=shift_title, 
                               shift_data=shift_data,
                               shift_user_points = shift_user_points[1],
                               ettermiddager = ettermiddager,
                               favoritt = favoritt,
                               page_name = 'Turnusdata for ' + shift_title)
    else:
        return "No shift data found", 400
    

@main.route('next_shift')
def next_shift():
    selected_shift = session.get('selected_shift')
    direction = request.args.get('direction')

    df_manager.df = df_manager.df.reset_index(drop=True)
    selected_shift_df = df_manager.df[df_manager.df['turnus'] == selected_shift]
    
    # Select the row after the filtered row
    
    if direction == 'next':
        next_row_index = selected_shift_df.index[0] + 1 if not selected_shift_df.empty else None
    elif direction == 'prev':
        next_row_index = selected_shift_df.index[0] - 1 if not selected_shift_df.empty else None
    else:
        return "Invalid direction", 400

    next_row = df_manager.df.iloc[next_row_index] if next_row_index is not None and next_row_index < len(df_manager.df) else None
    print(session.get('selected_shift'), next_row['turnus'])
    session['selected_shift'] = next_row['turnus']
    
    return redirect(url_for('main.display_shift'))


@main.route('/rate_displayed_shift', methods=['POST'])
def rate_displayed_shift():

    shift_title = session.get('shift_title')
    previous_user_point_input = session.get('current_user_point_input')
    new_user_points_input = int(request.form.get('user_points'))
    db_ctrl.set_user_points(df_manager.user_id, shift_title, new_user_points_input)
 
    df_manager.df.loc[df_manager.df['turnus'] == shift_title, 'poeng'] += (new_user_points_input - previous_user_point_input[1])
   

    return redirect(url_for('main.display_shift'))


@main.route('/download_excel')
def download_excel():
    filename = 'turnuser_R24.xlsx'  # Replace with your actual file name
    return send_from_directory(conf.static_dir, filename, as_attachment=True)


@main.route('/favorites')
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
                           page_name = 'Favoritter',
                           favorites = fav_dict_sorted,
                           dataframe = data)


@main.route('/update-order', methods=['POST'])
def update_order():
    data = request.get_json()
    new_order = data.get('order', [])
    user_id = current_user.get_id()
    shifts_to_add = None
    shifts_to_remove = None
    

    try:
        # Fetch the current order of the favorites
        query_fetch_order = """
        SELECT id, shift_title FROM favorites WHERE user_id = %s
        """
        current_database_order = db_utils.execute_query(query_fetch_order, (user_id, ), fetch='fetchall')
        current_shift_titles = {shift[1] for shift in current_database_order}
        print('current db order', current_database_order)

        # Determine which shift titles are missing in the new order
        new_shift_titles = set(new_order)
        shifts_to_remove = current_shift_titles - new_shift_titles
        shifts_to_add = new_shift_titles - current_shift_titles
        

        # Remove missing shift titles from the database
        if shifts_to_remove:
            query_delete_shifts = """
            DELETE FROM favorites WHERE user_id = %s AND shift_title IN (%s)
            """ % (user_id, ','.join(['%s'] * len(shifts_to_remove)))
            db_utils.execute_query(query_delete_shifts, tuple(shifts_to_remove))
        
        for shift_title in shifts_to_add:
            query_add_shift = """
            INSERT INTO favorites (shift_title, user_id, order_index)
            VALUES (%s, %s, %s)
            """
            db_utils.execute_query(query_add_shift, (shift_title, user_id, new_order.index(shift_title)))

        # update curent favorties order in database
        for index, shift_title in enumerate(new_order):
            query_update_order = """
            INSERT INTO favorites (shift_title, user_id, order_index)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE order_index = VALUES(order_index)
            """
            db_utils.execute_query(query_update_order, (shift_title, user_id, index))
    except Error as e:
        print(f"Failed to modify database. Changes only stored localy.")
        flash('Failed to modify database. Changes only stored localy. Error: {e}', 'danger')

    # Return a JSON response
    return jsonify({'status': 'success', 'new_order': new_order})


@main.route('/remove_favorite/<shift_title>', methods=['GET'])
def remove_favorite(shift_title):
    try:
        db_utils.remove_favorite(current_user.get_id(), shift_title)
    except ValueError:
        print('Not a favorite')
    return redirect(url_for('main.favorites'))



@main.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json()
    favorite = data.get('favorite')
    shift_title = data.get('shift_title')


    if favorite:
        max_order_index = db_utils.get_max_ordered_index(current_user.get_id())
        new_order_index = max_order_index +1 if max_order_index is not None else 1
        db_utils.add_favorite(current_user.get_id(),shift_title, new_order_index)
    else:
        print(f"Checkbox is unchecked. Title: {shift_title}.")
        try:
            db_utils.remove_favorite(current_user.get_id(), shift_title)
        except ValueError:
            print('Not a favorite')
    return jsonify({'status': 'success'})


df_manager = df_utils.DataframeManager()
db_ctrl = db_utils