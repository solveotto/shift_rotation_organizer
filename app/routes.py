import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_login import login_user as flask_login_user
from mysql.connector import Error

from config import conf
from app.utils import df_utils, db_utils
from app.forms import LoginForm
from app.models import User


main = Blueprint('main', __name__)
with open(os.path.join(conf.static_dir, 'turnuser_R24.json'), 'r') as f:
            stats_df = json.load(f)


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
                return redirect(url_for('main.home'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        except Error as e:
            print(f'Error: {e}')

    else:
        print("ERROR", form.errors)
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def home(): 
    # Convert DataFrame to a list of dictionaries
    ## table_data = df_manager.df.to_dict(orient='records')


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
                           page_name = 'Sorter turnuser'
                           )


@main.route('/navigate_home')
@login_required
def navigate_home():
    #df_manager.sort_by('poeng')
    return redirect(url_for('main.home'))


@main.route('/reset_search')
@login_required
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
@login_required
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

    tidlig = request.form.get('tidlig')
    tidlig_poeng = request.form.get('tidlig_poeng')
    session['tidlig']= tidlig
    session['tidlig_poeng'] = tidlig_poeng
    df_manager.calc_thresholds('tidlig', int(tidlig), int(tidlig_poeng))

    before_6 = request.form.get('before_6')
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
    nights_pts = request.form.get('nights_pts')
    session['nights'] = nights
    session['nights_pts'] = nights_pts
    df_manager.calc_thresholds('natt', int(nights), int(nights_pts))

    df_manager.get_all_user_points()
    df_manager.sort_by('poeng')
    
    return redirect(url_for('main.home'))


@main.route('/sort_by_column')
@login_required
def sort_by_column():
    column = request.args.get('column')
    if column in df_manager.df:
        df_manager.sort_by(column)
    else:
        df_manager.sort_by('poeng')

    return redirect(url_for('main.home'))



# This function is used by a javascript to make every line clickeable in the sorting view
@main.route('/api/select_shift', methods=['POST'])
@login_required
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
    for x in stats_df:
        for title, data in x.items():
            if title == selected_shift:
                shift_title = title
                shift_data = data
   
    shift_user_points = db_ctrl.get_shift_rating(df_manager.user_id, shift_title)
    session['current_user_point_input'] = shift_user_points
    session['shift_title'] =shift_title
    


    if shift_title and shift_data:
        return render_template('selected_shift.html',
                               table_data = selected_shift_df.to_dict(orient='records'), 
                               shift_title=shift_title, 
                               shift_data=shift_data,
                               shift_user_points = shift_user_points[1],
                               ettermiddager = ettermiddager,
                               page_name = 'Turnusdata for ' + shift_title)
    else:
        return "No shift data found", 400
    

@main.route('next_shift', methods=['POST'])
@login_required
def next_shift():
    selected_shift = session.get('selected_shift')
    direction = request.form.get('direction')

    selected_shift_df = df_manager.df[df_manager.df['turnus'] == selected_shift]
    
    # Select the row after the filtered row
    df_manager.df = df_manager.df.reset_index(drop=True)
    next_row_index = selected_shift_df.index[0] + 1 if not selected_shift_df.empty else None
    
    if direction == 'next':
        next_row_index = selected_shift_df.index[0] + 1 if not selected_shift_df.empty else None
    elif direction == 'prev':
        next_row_index = selected_shift_df.index[0] - 1 if not selected_shift_df.empty else None
    else:
        return "Invalid direction", 400

    next_row = df_manager.df.iloc[next_row_index] if next_row_index is not None and next_row_index < len(df_manager.df) else None
    session['selected_shift'] = next_row['turnus']
    
    return redirect(url_for('main.display_shift'))


@main.route('/rate_displayed_shift', methods=['POST'])
@login_required
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



df_manager = df_utils.DataframeManager()
db_ctrl = db_utils