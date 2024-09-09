import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_login import login_user as flask_login_user
from mysql.connector import Error

from config import Config
from app.utils import df_utils, db_utils
from app.forms import LoginForm
from app.models import User


main = Blueprint('main', __name__)


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
    df_manager.helgetimer = session.get('helgetimer', '0')
    helgetimer_dagtid = session.get('helgetimer_dagtid', '0')
    ettermiddager = session.get('ettermiddager', '0')
    ettermiddager_poeng = session.get('ettermiddager_poeng', '0')
    nights = session.get('nights', '0')
    nights_pts = session.get('nights_pts', '0')

    sort_btn_name = df_manager.sort_by_btn_txt

     # Pass the table data to the template
    return render_template('sort_shifts.html', 
                           table_data = df_manager.df.to_dict(orient='records'), 
                           helgetimer = df_manager.helgetimer,
                           helgetimer_dagtid = helgetimer_dagtid,
                           ettermiddager = ettermiddager,
                           ettermiddager_poeng = ettermiddager_poeng,
                           nights = nights,
                           nights_pts = nights_pts,
                           sort_by_btn_name = sort_btn_name
                           )


@main.route('/navigate_home')
@login_required
def navigate_home():
    #df_manager.sort_by('poeng')
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

    # calculate points for ettermiddager
    ettermiddager = request.form.get('ettermiddager', '0')
    ettermiddager_pts = request.form.get('ettermiddager_poeng', '0')
    session['ettermiddager'] = ettermiddager
    session['ettermiddager_poeng'] = ettermiddager_pts
    df_manager.calc_thresholds('ettermiddag', int(ettermiddager), int(ettermiddager_pts))
    

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


@main.route('/reset_search')
@login_required
def reset_search():
    session.clear()
    df_manager.df['poeng'] = 0
    df_manager.get_all_user_points()
    df_manager.sort_by('turnus', inizialize=True)
    return redirect(url_for('main.home'))


@main.route('/api/receive-data', methods=['POST'])
@login_required
def receive_data():
    html_data = request.get_json()
    selected_shift = html_data.get('turnus')

    with open(os.path.join(Config.static_dir, 'turnuser_R24.json'), 'r') as f:
            turnus_data = json.load(f)
    
    for x in turnus_data:
        for shift_title, shift_data in x.items():
            if shift_title == selected_shift:
                session['shift_title'] = shift_title
                session['shift_data'] = shift_data
                break
    return redirect(url_for('main.display_shift'))


@main.route('/display_shift')
@login_required
def display_shift():
    shift_title = session.get('shift_title')
    shift_data = session.get('shift_data')
    ettermiddager = session.get('ettermiddager')

    shift_user_points = db_ctrl.get_shift_rating(df_manager.user_id, shift_title)
    session['current_user_point_input'] = shift_user_points
    
    if shift_title and shift_data:
        return render_template('turnus.html',
                               table_data = df_manager.df.to_dict(orient='records'), 
                               shift_title=shift_title, 
                               shift_data=shift_data,
                               shift_user_points = shift_user_points[1],
                               ettermiddager = ettermiddager)
    else:
        return "No shift data found", 400
    
@main.route('/rate_displayed_shift', methods=['POST'])
@login_required
def rate_displayed_shift():

    shift_title = session.get('shift_title')
    previous_user_point_input = session.get('current_user_point_input')
    new_user_points_input = int(request.form.get('user_points'))
    db_ctrl.set_user_points(df_manager.user_id, shift_title, new_user_points_input)

    df_manager.df.loc[df_manager.df['turnus'] == shift_title, 'poeng'] += (new_user_points_input - previous_user_point_input[1])
   

    return redirect(url_for('main.display_shift'))



df_manager = df_utils.DataframeManager()
db_ctrl = db_utils