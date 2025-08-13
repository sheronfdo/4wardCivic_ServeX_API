"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app.services.user_service import UserService
from app.utils.validators import validate_user_data
from app.services.authority_service import AuthorityService
from app.models.authority import Authority

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/authority/register', methods=['POST'])
def register_authority():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    authority_id = AuthorityService.create_authority(
        data['authorityName'],
        data['email'],
        data['address'],
        data['phoneNumber'],
        data['hotline'],
        data.get('authorityIconId')
    )
    return jsonify({'id': authority_id}), 201

@auth_bp.route('/authority/admin/register', methods=['POST'])
def register_authority_admin():
    data = request.get_json()
    authority_obj = None

    # Get authority by ID
    if data.get('authority_id'):
        authority_obj = Authority.objects(id=data['authority_id']).first()
        if not authority_obj:
            return jsonify({'message': 'Invalid authority ID'}), 400

    # Or get authority by email
    elif data.get('authority_email'):
        authority_obj = Authority.objects(email=data['authority_email']).first()
        if not authority_obj:
            return jsonify({'message': 'Authority with given email not found'}), 404

    # No authority provided at all
    else:
        return jsonify({'message': 'Authority ID or email is required'}), 400

    # Create admin user
    result = UserService.create_authority_user({
        'name': data.get('name', 'Authority Admin'),
        'email': data['email'],
        'password': data['password'],
        'authority': authority_obj  # pass object, not ID
    })

    if result['success']:
        return jsonify({'message': 'Admin registered', 'user': result['data']}), 201
    else:
        return jsonify({'message': result['message']}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Authenticate user
        auth_result = user_service.authenticate_user(email, password)
        
        if not auth_result['success']:
            return jsonify({'message': auth_result['message']}), 401
        
        user_data = auth_result['data']
        
        # Check if user is Admin (as per your original requirement)
        if user_data['role'] != 'Admin':
            return jsonify({'message': 'Access denied: Admins only'}), 403
        
        # Create access token
        access_token = create_access_token(identity=user_data['id'])
        
        return jsonify({
            'token': access_token,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = user_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'valid': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500

#
# @auth_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     """Get current user profile"""
#     try:
#         current_user_id = get_jwt_identity()
#         user = user_service.get_user_by_id(current_user_id)
#
#         if not user:
#             return jsonify({'message': 'User not found'}), 404
#
#         return jsonify({'user': user.to_dict()}), 200
#
#     except Exception as e:
#         return jsonify({'message': str(e)}), 500
#
#
# @auth_bp.route('/profile', methods=['PUT'])
# @jwt_required()
# def update_profile():
#     """Update current user profile"""
#     try:
#         current_user_id = get_jwt_identity()
#         data = request.get_json()
#
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
#
#         # Update user through service
#         result = user_service.update_user(current_user_id, data)
#
#         if result['success']:
#             return jsonify({
#                 'message': result['message'],
#                 'user': result['data']
#             }), 200
#         else:
#             return jsonify({'message': result['message']}), 400
#
#     except Exception as e:
#         return jsonify({'message': str(e)}), 500
#
#
# @auth_bp.route('/change-password', methods=['PUT'])
# @jwt_required()
# def change_password():
#     """Change current user password"""
#     try:
#         current_user_id = get_jwt_identity()
#         data = request.get_json()
#
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
#
#         current_password = data.get('current_password')
#         new_password = data.get('new_password')
#
#         if not current_password or not new_password:
#             return jsonify({'message': 'Current and new passwords are required'}), 400
#
#         # Change password through service
#         result = user_service.change_password(current_user_id, current_password, new_password)
#
#         if result['success']:
#             return jsonify({'message': result['message']}), 200
#         else:
#             return jsonify({'message': result['message']}), 400
#
#     except Exception as e:
#         return jsonify({'message': str(e)}), 500