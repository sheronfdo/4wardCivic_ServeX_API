"""
Process routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.decorators import role_required
from app.services.process_service import ProcessService


process_bp = Blueprint('process', __name__)
user_service = UserService()


@process_bp.route('/<service_id>', methods=['GET'])  # Added GET route for fetching rolls
@jwt_required()
@role_required('GovAdmin','GovStaff')
def get_rolls(service_id):
    """Get all process for Service"""
    try:
        
       
        # Get rolls for this authority
        result = ProcessService.get_processes_by_service(service_id)
        
        if result['success']:
            return jsonify({
                'message': 'process fetched successfully',
                'data': result
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error fetching process: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

 