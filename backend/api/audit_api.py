from flask import Blueprint, jsonify, request, session, g, render_template, send_file, current_app
from backend.core.audit_manager import AuditManager
from functools import wraps
import csv
import io
import pandas as pd
from datetime import datetime

audit_bp = Blueprint('audit_bp', __name__, url_prefix='/api/audit')

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = str(session.get('role', 'User')).lower()
        if role not in ['admin', 'super_admin', 'test admin']:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@audit_bp.route('/')
@require_company_context
@admin_required
def view_audit_logs():
    return render_template('audit_logs.html')

@audit_bp.route('/data', methods=['GET'])
@require_company_context
@admin_required
def get_audit_data():
    try:
        manager = AuditManager()
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Determine if we should filter by company
        # Super admins might want to see everything, but for multi-tenancy, usually restricted.
        # We will strictly filter by company_id for now to be safe.
        rows = manager.get_logs(limit=limit, offset=offset, company_id=g.company_id)
        logs = [dict(row) for row in rows]
        
        # Get total count for pagination
        total = manager.get_logs_count(company_id=g.company_id)
        
        return jsonify({'logs': logs, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@audit_bp.route('/export', methods=['GET'])
@require_company_context
@admin_required
def export_audit_logs():
    try:
        format_type = request.args.get('format', 'csv')
        limit = request.args.get('limit', 1000, type=int)
        
        manager = AuditManager()
        logs = manager.get_logs(limit=limit, offset=0, company_id=g.company_id)
        
        if not logs:
            return jsonify({'error': 'No logs found to export'}), 404
            
        # Convert to list of dicts if not already
        data = [dict(log) for log in logs]
        
        if format_type == 'csv':
            output = io.StringIO()
            if data:
                keys = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
            
        elif format_type == 'excel':
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Audit Logs')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
