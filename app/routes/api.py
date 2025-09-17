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

@api.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.get_json()
    favorite = data.get('favorite')
    shift_title = data.get('shift_title')

    with favorite_lock:
        try:
            if favorite:
                # Calculate the next order index for the new favorite
                order_index = db_utils.get_max_ordered_index(current_user.get_id()) + 1
                db_utils.add_favorite(current_user.get_id(), shift_title, order_index)
                return jsonify({'status': 'success', 'message': 'Added to favorites'})
            else:
                db_utils.remove_favorite(current_user.get_id(), shift_title)
                return jsonify({'status': 'success', 'message': 'Removed from favorites'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

@api.route('/move-favorite', methods=['POST'])
def move_favorite():
    data = request.get_json()
    shift_title = data.get('shift_title')
    direction = data.get('direction')
    user_id = current_user.get_id()
    
    if not shift_title or direction not in ['up', 'down']:
        return jsonify({'status': 'error', 'message': 'Invalid parameters'})
    
    try:
        session = db_utils.get_db_session()
        
        # Get current favorites with order
        current_favorites = session.query(db_utils.Favorites).filter_by(user_id=user_id).order_by(db_utils.Favorites.order_index).all()
        
        if not current_favorites:
            session.close()
            return jsonify({'status': 'error', 'message': 'No favorites found'})
        
        # Find current position
        current_index = None
        for i, favorite in enumerate(current_favorites):
            if favorite.shift_title == shift_title:
                current_index = i
                break
        
        if current_index is None:
            session.close()
            return jsonify({'status': 'error', 'message': 'Favorite not found'})
        
        # Calculate new position
        if direction == 'up' and current_index > 0:
            new_index = current_index - 1
        elif direction == 'down' and current_index < len(current_favorites) - 1:
            new_index = current_index + 1
        else:
            session.close()
            return jsonify({'status': 'error', 'message': 'Cannot move in that direction'})
        
        # Swap the order_index values
        current_favorite = current_favorites[current_index]
        target_favorite = current_favorites[new_index]
        
        # Store the current order_index values
        temp_order = current_favorite.order_index
        current_favorite.order_index = target_favorite.order_index
        target_favorite.order_index = temp_order
        
        # Commit the changes
        session.commit()
        session.close()
        
        return jsonify({'status': 'success', 'message': 'Favorite moved successfully'})
        
    except Exception as e:
        if 'session' in locals():
            session.rollback()
            session.close()
        print(f"Error moving favorite: {e}")
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}) 