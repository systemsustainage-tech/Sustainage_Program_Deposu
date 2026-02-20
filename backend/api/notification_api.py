from flask import Blueprint, jsonify, request, session, g, render_template
from backend.modules.notification.notification_manager import NotificationManager
from functools import wraps

# Local decorator to avoid circular imports
def require_company_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        company_id = session.get('company_id')
        if isinstance(company_id, dict):
             company_id = company_id.get('id') or company_id.get('company_id')
             session['company_id'] = company_id
             
        if not company_id:
            return jsonify({'error': 'No company context'}), 403
            
        g.company_id = int(company_id)
        return f(*args, **kwargs)
    return decorated_function

notification_bp = Blueprint('notification_bp', __name__, url_prefix='/api/notifications')

@notification_bp.route('/unread', methods=['GET'])
@require_company_context
def get_unread():
    try:
        manager = NotificationManager(company_id=g.company_id)
        user_id = session.get('user_id')
        limit = request.args.get('limit', 5, type=int)
        
        notifications = manager.get_unread_notifications(user_id, limit=limit, company_id=g.company_id)
        count = manager.get_unread_count(user_id, company_id=g.company_id)
        
        return jsonify({'notifications': notifications, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/all', methods=['GET'])
@require_company_context
def get_all():
    try:
        manager = NotificationManager(company_id=g.company_id)
        user_id = session.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        
        notifications = manager.get_all_notifications(user_id, limit=limit, company_id=g.company_id)
        return jsonify(notifications)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/', methods=['GET'])
@require_company_context
def view_notifications():
    return render_template('notifications.html')

@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@require_company_context
def mark_read(notification_id):
    try:
        manager = NotificationManager(company_id=g.company_id)
        manager.mark_as_read(notification_id, company_id=g.company_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/mark-all-read', methods=['POST'])
@require_company_context
def mark_all_read():
    try:
        manager = NotificationManager(company_id=g.company_id)
        user_id = session.get('user_id')
        manager.mark_all_as_read(user_id, company_id=g.company_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
