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

@api.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.get_json()
    favorite = data.get('favorite')
    shift_title = data.get('shift_title')

    with favorite_lock:
        try:
            # Get user's selected turnus set
            from app.routes.shifts import get_user_turnus_set
            user_turnus_set = get_user_turnus_set()
            turnus_set_id = user_turnus_set['id'] if user_turnus_set else None
            
            if not turnus_set_id:
                return jsonify({'status': 'error', 'message': 'No turnus set selected'})
            
            if favorite:
                # Calculate the next order index for the user's selected turnus set
                order_index = db_utils.get_max_ordered_index(current_user.get_id(), turnus_set_id) + 1
                success = db_utils.add_favorite(current_user.get_id(), shift_title, order_index, turnus_set_id)
                if success:
                    return jsonify({'status': 'success', 'message': 'Added to favorites'})
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to add favorite'})
            else:
                success = db_utils.remove_favorite(current_user.get_id(), shift_title, turnus_set_id)
                if success:
                    return jsonify({'status': 'success', 'message': 'Removed from favorites'})
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to remove favorite'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

@api.route('/move-favorite', methods=['POST'])
@login_required
def move_favorite():
    data = request.get_json()
    shift_title = data.get('shift_title')
    direction = data.get('direction')
    user_id = current_user.get_id()
    
    if not shift_title or direction not in ['up', 'down']:
        return jsonify({'status': 'error', 'message': 'Invalid parameters'})
    
    try:
        # Get user's selected turnus set
        from app.routes.shifts import get_user_turnus_set
        user_turnus_set = get_user_turnus_set()
        turnus_set_id = user_turnus_set['id'] if user_turnus_set else None
        
        if not turnus_set_id:
            return jsonify({'status': 'error', 'message': 'No turnus set selected'})
        
        session = db_utils.get_db_session()
        
        # Get current favorites with order FOR THE SPECIFIC TURNUS SET
        current_favorites = session.query(db_utils.Favorites).filter_by(
            user_id=user_id, 
            turnus_set_id=turnus_set_id
        ).order_by(db_utils.Favorites.order_index).all()
        
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
        return jsonify({'status': 'error', 'message': str(e)}) 