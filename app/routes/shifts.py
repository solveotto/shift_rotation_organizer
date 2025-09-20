import time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from app.utils import db_utils
from app.routes.main import df_manager, turnus_data

shifts = Blueprint('shifts', __name__)


@shifts.route('/')
@login_required
def turnusliste():
    # Get favorites for current user
    favoritt = db_utils.get_favorite_lst(current_user.get_id()) if current_user.is_authenticated else []
    
    return render_template('turnusliste.html', 
                         page_name='Turnusliste',
                         table_data=turnus_data,  
                         df=df_manager.df.to_dict(orient='records'), 
                         favoritt=favoritt)  



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


@shifts.route('/compare')
@login_required
def compare():
    # Prepare metrics for charts
    df = df_manager.df
    metrics = ['natt', 'tidlig', 'shift_cnt', 'before_6', 'helgetimer']
    labels = df['turnus'].tolist()
    data = {m: df[m].tolist() if m in df else [] for m in metrics}

    return render_template(
        'compare.html',
        page_name='Sammenlign Turnuser',
        labels=labels,
        data=data
    )
