from flask import Blueprint, request, jsonify, g, current_app, send_file, session
import os
import logging
import tempfile
from functools import wraps

# Local decorator to avoid circular imports and dependency issues
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

file_bp = Blueprint('file_api', __name__, url_prefix='/api/files')

def get_manager():
    """Get the initialized AdvancedFileManager from app config"""
    return current_app.config.get('MANAGERS', {}).get('file_manager')

@file_bp.route('/tags', methods=['GET'])
@require_company_context
def list_tags():
    """List all tags for the company"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    try:
        tags = manager.get_all_tags(company_id=g.company_id)
        return jsonify(tags)
    except Exception as e:
        logging.error(f"List tags error: {e}")
        return jsonify({'error': str(e)}), 500

@file_bp.route('/', methods=['GET'])
@require_company_context
def list_files():
    """List files with optional filtering"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    folder_id = request.args.get('folder_id', type=int)
    search = request.args.get('search', '')
    tags = request.args.getlist('tags')
    
    try:
        files = manager.list_files(
            company_id=g.company_id,
            folder_id=folder_id,
            search_term=search,
            tags=tags
        )
        return jsonify(files)
    except Exception as e:
        logging.error(f"List files error: {e}")
        return jsonify({'error': str(e)}), 500

@file_bp.route('/upload', methods=['POST'])
@require_company_context
def upload_file():
    """Upload a new file"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    folder_id = request.form.get('folder_id', type=int)
    description = request.form.get('description', '')
    # Handle tags (comma separated string or multiple values)
    tags_raw = request.form.get('tags')
    tags = []
    if tags_raw:
        if ',' in tags_raw:
            tags = [t.strip() for t in tags_raw.split(',')]
        else:
            tags = [tags_raw.strip()]
    
    temp_path = None
    try:
        # Save securely to temp file
        fd, temp_path = tempfile.mkstemp()
        os.close(fd)
        file.save(temp_path)
        
        user_id = g.user.get('id') if hasattr(g, 'user') and g.user else None
        
        file_id = manager.upload_file(
            company_id=g.company_id,
            source_path=temp_path,
            folder_id=folder_id,
            description=description,
            tags=tags,
            uploaded_by=user_id
        )
        
        if file_id:
            return jsonify({'message': 'File uploaded successfully', 'id': file_id}), 201
        else:
            return jsonify({'error': 'Upload failed'}), 500
            
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

@file_bp.route('/folders', methods=['POST'])
@require_company_context
def create_folder():
    """Create a new folder"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    data = request.json or {}
    name = data.get('name')
    parent_id = data.get('parent_id')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Folder name required'}), 400
        
    try:
        user_id = g.user.get('id') if hasattr(g, 'user') and g.user else None
        
        folder_id = manager.create_folder(
            company_id=g.company_id,
            name=name,
            parent_id=parent_id,
            description=description,
            created_by=user_id
        )
        
        if folder_id:
            return jsonify({'message': 'Folder created', 'id': folder_id}), 201
        else:
            return jsonify({'error': 'Folder creation failed'}), 500
    except Exception as e:
        logging.error(f"Folder creation error: {e}")
        return jsonify({'error': str(e)}), 500

@file_bp.route('/folders', methods=['GET'])
@require_company_context
def list_folders():
    """List folders in a directory"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    parent_id = request.args.get('parent_id', type=int)
    
    try:
        folders = manager.list_folders(
            company_id=g.company_id,
            parent_id=parent_id
        )
        return jsonify(folders)
    except Exception as e:
        logging.error(f"List folders error: {e}")
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<int:file_id>', methods=['DELETE'])
@require_company_context
def delete_file(file_id):
    """Delete a file"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    try:
        user_id = g.user.get('id') if hasattr(g, 'user') and g.user else None
        
        success = manager.delete_file(
            company_id=g.company_id,
            file_id=file_id,
            deleted_by=user_id
        )
        if success:
            return jsonify({'message': 'File deleted'})
        else:
            return jsonify({'error': 'Delete failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@require_company_context
def delete_folder(folder_id):
    """Delete a folder"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    try:
        user_id = g.user.get('id') if hasattr(g, 'user') and g.user else None
        
        success = manager.delete_folder(
            company_id=g.company_id,
            folder_id=folder_id,
            deleted_by=user_id
        )
        if success:
            return jsonify({'message': 'Folder deleted'})
        else:
            return jsonify({'error': 'Delete failed (folder might not be empty)'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/download/<int:file_id>', methods=['GET'])
@require_company_context
def download_file(file_id):
    """Download a file"""
    manager = get_manager()
    if not manager:
        return jsonify({'error': 'File manager not initialized'}), 503
        
    try:
        file_info = manager.get_file_info(file_id, company_id=g.company_id)
        if not file_info:
            return jsonify({'error': 'File not found'}), 404
            
        file_path = file_info.get('path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info.get('name')
        )
            
    except Exception as e:
        logging.error(f'Download error: {e}')
        return jsonify({'error': str(e)}), 500

