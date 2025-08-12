"""
User CRUD routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.validators import validate_pagination_params, validate_search_params

user_bp = Blueprint('users', __name__)
user_service = UserService()


@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', '1')
        limit = request.args.get('limit', '10')
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        
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
            return jsonify(result['data']), 200
        else:
            return jsonify({'message': result['message']}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user by ID"""
    try:
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Create user through service
        result = user_service.create_user(data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['data']
            }), 201
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500


@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user by ID"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update user through service
        result = user_service.update_user(user_id, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['data']
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user by ID"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent users from deleting themselves
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


@user_bp.route('/<user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent users from deactivating themselves
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


@user_bp.route('/<user_id>/role', methods=['PATCH'])
@jwt_required()
def update_user_role(user_id):
    """Update user role"""
    try:
        data = request.get_json()
        
        if not data or 'role' not in data:
            return jsonify({'message': 'Role is required'}), 400
        
        # Update role through service
        result = user_service.update_user(user_id, {'role': data['role']})
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['data']
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    try:
        result = user_service.get_user_stats()
        
        if result['success']:
            return jsonify(result['data']), 200
        else:
            return jsonify({'message': result['message']}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500