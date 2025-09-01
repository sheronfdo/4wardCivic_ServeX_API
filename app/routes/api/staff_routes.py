"""
Staff routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.decorators import role_required
from app.services.staff_roll_service import StaffRollService
from app.models.user import User

staff_bp = Blueprint('staff', __name__)
user_service = UserService()

@staff_bp.route('/roll/create', methods=['POST'])  # Fixed route path
@jwt_required()
@role_required('GovAdmin')
def create_roll():
    """Create a new staff roll"""
    try:
        roll_data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate current user
        if not current_user_id:
            return jsonify({'message': 'User ID is required'}), 400
            
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if not user.authority:
            return jsonify({'message': 'User authority not found'}), 400
    
        # Validate roll data
        if not roll_data:
            return jsonify({'message': 'No roll data provided'}), 400
        
        # Create staff roll
        result = StaffRollService.create_roll_for_staff(user.authority.id, roll_data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'roll': result.get('data')
            }), 201
        else:
            return jsonify({
                'message': result['message'],
                'errors': result.get('errors', [])
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error creating staff roll: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@staff_bp.route('/rolls', methods=['GET'])  # Added GET route for fetching rolls
@jwt_required()
@role_required('GovAdmin')
def get_rolls():
    """Get all staff rolls for current user's authority"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validate current user
        if not current_user_id:
            return jsonify({'message': 'User ID is required'}), 400
            
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if not user.authority:
            return jsonify({'message': 'User authority not found'}), 400
        
        # Get rolls for this authority
        result = StaffRollService.get_rolls_by_authority(user.authority.id)
        
        if result['success']:
            return jsonify({
                'message': 'Rolls fetched successfully',
                'rolls': result['data']
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error fetching staff rolls: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@staff_bp.route('/staff-list', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_roll_staff():
    """Get all staff members for the current authority admin"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the current admin user
        admin_user = User.objects(id=current_user_id).first()
        if not admin_user:
            return jsonify({'message': 'Admin user not found'}), 404
        
        if not admin_user.authority:
            return jsonify({'message': 'Admin user has no authority assigned'}), 400
        
        # Get staff list from service
        result = StaffRollService.get_authority_staff_list(str(admin_user.authority.id))
        
        if result['success']:
            return jsonify({
                'message': 'Staff list retrieved successfully',
                'staff_list': result['data'],
                'total_count': result['total_count'],
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error retrieving staff list: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@staff_bp.route('/staff-list/<roll_id>', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_authority_staff(roll_id):
    """Get all staff members for the current roll"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the current admin user
        admin_user = User.objects(id=current_user_id).first()
        if not admin_user:
            return jsonify({'message': 'Admin user not found'}), 404
        
        if not admin_user.authority:
            return jsonify({'message': 'Admin user has no authority assigned'}), 400
        
        # Get staff list from service
        result = StaffRollService.get_staff_list_by_roll(roll_id)
        
        if result['success']:
            return jsonify({
                'message': 'Staff list retrieved successfully',
                'staff_list': result['data'],
                'total_count': result['total_count'],
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error retrieving staff list: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500