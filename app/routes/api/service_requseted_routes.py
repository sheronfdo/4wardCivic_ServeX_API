from flask import Blueprint, request, jsonify
from app.services.form_service import FormService
from app.models.service import Service
from app.models.form import Form
import re
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required
from app.services.service_requested_service import ServiceRequestedService
# Create blueprint for service requested routes
service_requsted_bp = Blueprint('service_requested', __name__, url_prefix='/servicerequested')

def validate_object_id(id_string):
    """Validate if string is a valid MongoDB ObjectId"""
    return re.match(r'^[0-9a-fA-F]{24}$', id_string) is not None

@service_requsted_bp.route('/create', methods=['POST'])
@jwt_required()
@role_required('Citizen','GovAdmin')
def create_requested_Service():
    """Create a new requested service"""
    try:
        current_user_Id = get_jwt_identity()
        

        if not current_user_Id :
            return jsonify({"error": "User Not Found "}), 403
        data = request.get_json()
        data["user_id"] = str(current_user_Id)

        if not data:
            return jsonify({"error": "No data provided"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        
        result = ServiceRequestedService.create_rqested_service(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
    
