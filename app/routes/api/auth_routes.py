"""
Authentication routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app.services.user_service import UserService
from app.utils.decorators import role_required
from app.utils.validators import validate_user_data
from app.services.authority_service import AuthorityService
from app.models.authority import Authority
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/authority/register', methods=['POST'])
def register_authority():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    try:
        authority_id = AuthorityService.create_authority(
            data['authorityName'],
            data['email'],
            data['address'],
            data['phoneNumber'],
            data['hotline'],
            data['authorityIconId']
        )
        return jsonify({
            'message': 'Authority registered. Verification email sent.',
            'authority_id': authority_id
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error registering authority: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/authority/verify-email', methods=['GET'])
def verify_authority_email():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is required'}), 400

    try:
        authority_id = AuthorityService.verify_email(token)
        return jsonify({'message': 'Email verified successfully', 'authority_id': authority_id}), 200
    except Exception as e:
        current_app.logger.error(f"Error verifying authority email: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/authority/admin/register', methods=['POST'])
def register_authority_admin():
    data = request.get_json()
    authority_obj = None

    authority_id = data.get('authority_id')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', 'Admin')

    if not all([authority_id, email, password, name]):
        return jsonify({'message': 'Missing required fields'}), 400

    # Get authority by ID
    if authority_id:
        authority_obj = Authority.objects(id=authority_id).first()
        if not authority_obj:
            return jsonify({'message': 'Invalid authority ID'}), 400

    # No authority provided at all
    else:
        return jsonify({'message': 'Authority ID is required'}), 400
    try:
    # Create admin user
        result = UserService.create_authority_user({
            'name': data.get('name', 'Authority Admin'),
            'email': data['email'],
            'password': data['password'],
            'authority': authority_id  # pass object, not ID
        })
        if result['success']:
            return jsonify({'message': 'Admin registered. Verification email sent if needed.',
                            'user': result['data'],
                            'is_verification_needed': not(result['is_verified'])}), 201
        else:
            return jsonify({'message': result['message']}), 400

    except Exception as e:
        current_app.logger.error(f"Error registering admin: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/authority/admin/verify-email', methods=['GET'])
def verify_admin_email():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is required'}), 400
    try:
        response = UserService.verify_admin_email(token)
        authority_id = response['authority_id']
        user_id = response['user_id']
        if authority_id:
            AuthorityService.activate_authority(authority_id)
        return jsonify({'message': 'Admin email verified successfully', 'user_id': user_id}), 200
    except Exception as e:
        current_app.logger.error(f"Error verifying admin email: {str(e)}")
        return jsonify({'message': str(e)}), 400


@auth_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    """Handle Firebase Google Sign-In and issue custom JWT"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid Authorization header'}), 401

        id_token = auth_header.split('Bearer ')[1]
        try:
            decoded_token = auth.verify_id_token(id_token)
        except auth.InvalidIdTokenError as e:
            current_app.logger.error(f"Invalid Firebase ID token: {str(e)}")
            return jsonify({'message': 'Invalid Firebase ID token'}), 401
        except auth.ExpiredIdTokenError as e:
            current_app.logger.error(f"Firebase ID token has expired: {str(e)}")
            return jsonify({'message': 'Firebase ID token has expired'}), 401
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name', email.split('@')[0])

        if not email:
            return jsonify({'message': 'Email not found in Firebase token'}), 400

        user = user_service.find_by_email(email)
        signup_required = False
        if not user:
            # Create a new user with role 'User'
            user_data = {
                'name': name,
                'email': email,
                'role': 'Citizen',
                'password': '',  # No password for Firebase users
                'is_verified': True,  # Firebase verifies email
                'status': 'ACTIVE'
            }
            create_result = user_service.create_citizen_user(user_data)
            if not create_result['success']:
                return jsonify({'message': create_result['message']}), 400
            user = user_service.find_by_email(email)

        if not user.fullname or not user.id_type or not user.id_number or not user.phone_number:
            signup_required = True

        # if not user.is_active:
        #     return jsonify({'message': 'Account is deactivated'}), 403

        # Issue custom JWT token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'token': access_token,
            'user': user.to_dict(),
            'is_signup_required':signup_required
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error during Firebase login: {str(e)}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/citizen-registration', methods=['POST'])
@jwt_required()
@role_required('Citizen')
def citizen_registration():
    """Handle Firebase Google Sign-In and issue custom JWT"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        citizen_id = data['citizen_id']
        fullname = data['fullname']
        id_type = data['id_type']
        id_number = data['id_number']
        phone_number = data['phone_number']

        user_data = {
            'citizen_id':citizen_id,
            'fullname':fullname,
            'id_type': id_type,
            'id_number': id_number,
            'phone_number': phone_number,
        }

        result = user_service.citizen_registration_details(user_data)
        if not result['success']:
            return jsonify({'message': result['message']}), 400
        return jsonify({'success':True, }), 200
    except Exception as e:
        current_app.logger.error(f"Error during Firebase login: {str(e)}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

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
        if user_data['role'] != 'GovAdmin':
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