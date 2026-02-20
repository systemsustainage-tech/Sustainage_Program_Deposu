# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, g
from backend.core.role_manager import RoleManager
from backend.core.module_access import require_permission # If exists, or I create a decorator

role_bp = Blueprint('role_api', __name__, url_prefix='/api/roles')
rm = RoleManager()

@role_bp.route('/', methods=['GET'])
def list_roles():
    # Helper to list roles
    conn = rm.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, display_name, description FROM roles WHERE is_active = 1")
    roles = [{'id': r[0], 'name': r[1], 'display_name': r[2], 'description': r[3]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(roles)

@role_bp.route('/', methods=['POST'])
def create_role():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    role_id = rm.create_role(name, description)
    if role_id:
        return jsonify({'message': 'Role created', 'id': role_id}), 201
    else:
        return jsonify({'error': 'Failed to create role'}), 500

@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
def get_role_permissions(role_id):
    conn = rm.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.display_name 
        FROM role_permissions rp 
        JOIN permissions p ON rp.permission_id = p.id 
        WHERE rp.role_id = ?
    """, (role_id,))
    perms = [{'name': r[0], 'display_name': r[1]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(perms)

@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
def assign_permissions(role_id):
    data = request.json
    permissions = data.get('permissions', []) # List of permission names
    
    success_count = 0
    for perm_name in permissions:
        if rm.assign_permission_to_role(role_id, perm_name):
            success_count += 1
            
    return jsonify({'message': f'Assigned {success_count} permissions'}), 200

@role_bp.route('/permissions', methods=['GET'])
def list_all_permissions():
    conn = rm.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, display_name, module, action FROM permissions WHERE is_active = 1 ORDER BY module, name")
    perms = [{'id': r[0], 'name': r[1], 'display_name': r[2], 'module': r[3], 'action': r[4]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(perms)
