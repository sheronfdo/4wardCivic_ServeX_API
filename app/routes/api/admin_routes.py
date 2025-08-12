"""
Admin-specific routes with enhanced permissions
"""
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.validators import validate_pagination_params, validate_search_params

admin_bp = Blueprint('admin', __name__)
user_service = UserService()


def admin_required(f):
    """Decorator to ensure user has admin role"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = user_service.get_user_by_id(current_user_id)
        
        if not user or not user.is_admin():
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        stats_result = user_service.get_user_stats()
        
        if not stats_result['success']:
            return jsonify({'message': stats_result['message']}), 500
        
        # Get recent users (last 10)
        recent_users_result = user_service.get_all_users(page=1, limit=10)
        
        dashboard_data = {
            'stats': stats_result['data'],
            'recent_users': recent_users_result['data']['users'] if recent_users_result['success'] else []
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Admin endpoint to get all users with enhanced filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', '1')
        limit = request.args.get('limit', '20')  # Higher default limit for admin
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        status = request.args.get('status', '')  # active, inactive, all
        
        # Validate pagination parameters
        pagination_validation = validate_pagination_params(page, limit)
        if not pagination_validation['valid']:
            return jsonify({'message': pagination_validation['message']}), 400
        
        # Validate search parameters
        search_validation = validate_search_params(search)
        if not search_validation['valid']:
            return jsonify({'message': search_validation['message']}), 400
        
        # Get users through service
        result = user_service.get_all_users(
            page=pagination_validation['page'],
            limit=pagination_validation['limit'],
            search=search_validation.get('search'),
            role=role if role else None
        )
        
        if result['success']:
            # Additional filtering by status if requested
            if status in ['active', 'inactive']:
                users = result['data']['users']
                if status == 'active':
                    users = [user for user in users if user['is_active']]
                elif status == 'inactive':
                    users = [user for user in users if not user['is_active']]
                
                result['data']['users'] = users
            
            return jsonify(result['data']), 200
        else:
            return jsonify({'message': result['message']}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """Admin endpoint to delete any user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent admin from deleting themselves
        if current_user_id == user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        # Delete user through service
        result = user_service.delete_user(user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'message': result['message']}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users/<user_id>/role', methods=['PATCH'])
@admin_required
def admin_update_user_role(user_id):
    """Admin endpoint to update user role"""
    try:
        data = request.get_json()
        
        if not data or 'role' not in data:
            return jsonify({'message': 'Role is required'}), 400
        
        new_role = data['role']
        
        if new_role not in ['Admin', 'User']:
            return jsonify({'message': 'Invalid role. Must be Admin or User'}), 400
        
        # Update role through service
        result = user_service.update_user(user_id, {'role': new_role})
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['data']
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users/<user_id>/status', methods=['PATCH'])
@admin_required
def admin_toggle_user_status(user_id):
    """Admin endpoint to toggle user status"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent admin from changing their own status
        if current_user_id == user_id:
            return jsonify({'message': 'Cannot change your own status'}), 400
        
        # Toggle status through service
        result = user_service.toggle_user_status(user_id)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['data']
            }), 200
        else:
            return jsonify({'message': result['message']}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users/bulk-delete', methods=['DELETE'])
@admin_required
def admin_bulk_delete_users():
    """Admin endpoint to delete multiple users"""
    try:
        data = request.get_json()
        
        if not data or 'user_ids' not in data:
            return jsonify({'message': 'user_ids array is required'}), 400
        
        user_ids = data['user_ids']
        current_user_id = get_jwt_identity()
        
        if not isinstance(user_ids, list):
            return jsonify({'message': 'user_ids must be an array'}), 400
        
        # Prevent admin from deleting themselves
        if current_user_id in user_ids:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        deleted_count = 0
        errors = []
        
        for user_id in user_ids:
            result = user_service.delete_user(user_id)
            if result['success']:
                deleted_count += 1
            else:
                errors.append({'user_id': user_id, 'error': result['message']})
        
        response_data = {
            'message': f'Successfully deleted {deleted_count} users',
            'deleted_count': deleted_count,
            'total_requested': len(user_ids)
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users/export', methods=['GET'])
@admin_required
def admin_export_users():
    """Admin endpoint to export user data"""
    try:
        # Get all users without pagination for export
        result = user_service.get_all_users(page=1, limit=1000)  # Large limit for export
        
        if not result['success']:
            return jsonify({'message': result['message']}), 500
        
        users_data = result['data']['users']
        
        # Format data for export
        export_data = []
        for user in users_data:
            export_data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login': user['last_login']
            })
        
        return jsonify({
            'users': export_data,
            'total_count': len(export_data),
            'exported_at': user_service.get_user_stats()['data'] if user_service.get_user_stats()['success'] else None
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500