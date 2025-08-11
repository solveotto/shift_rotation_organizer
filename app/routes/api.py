from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from mysql.connector import Error
from app.utils import db_utils
from app.routes.main import favorite_lock

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/js_select_shift', methods=['POST'])
def select_shift():
    data = request.get_json()
    shift_title = data.get('shift_title')
    
    if shift_title:
        # Redirect to the display_shift page instead of returning JSON
        from flask import redirect, url_for
        return redirect(url_for('shifts.display_shift', shift_title=shift_title))
    else:
        return jsonify({'status': 'error', 'message': 'No shift title provided'})

@api.route('/rate_displayed_shift', methods=['POST'])
def rate_displayed_shift():
    data = request.get_json()
    shift_title = data.get('shift_title')
    rating = data.get('rating')
    
    if not shift_title or rating is None:
        return jsonify({'status': 'error', 'message': 'Missing shift_title or rating'})
    
    try:
        db_utils.save_rating(current_user.get_id(), shift_title, rating)
        return jsonify({'status': 'success', 'message': 'Rating saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to save rating: {str(e)}'})

@api.route('/update-order', methods=['POST'])
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

        # update current favorites order in database
        for index, shift_title in enumerate(new_order):
            query_update_order = """
            INSERT INTO favorites (shift_title, user_id, order_index)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE order_index = VALUES(order_index)
            """
            db_utils.execute_query(query_update_order, (shift_title, user_id, index))
    except Error as e:
        print(f"Failed to modify database. Changes only stored locally.")
        return jsonify({'status': 'error', 'message': f'Failed to modify database. Changes only stored locally. Error: {e}'})

    return jsonify({'status': 'success', 'new_order': new_order})

@api.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json()
    favorite = data.get('favorite')
    shift_title = data.get('shift_title')

    with favorite_lock:
        try:
            if favorite:
                db_utils.add_favorite(current_user.get_id(), shift_title)
                return jsonify({'status': 'success', 'message': 'Added to favorites'})
            else:
                db_utils.remove_favorite(current_user.get_id(), shift_title)
                return jsonify({'status': 'success', 'message': 'Removed from favorites'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}) 