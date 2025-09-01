from flask import Blueprint, request, jsonify
from app.services.form_service import FormService
from app.models.service import Service
from app.models.form import Form
import re
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required
from app.services.service_requested_service import ServiceRequestedService
from app.models.service import Service
from app.models.user import User
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

@service_requsted_bp.route('/requested', methods=['GET'])
@jwt_required()
@role_required('GovAdmin','Citizen')
def get_requested_services():
    """Get all services linked to forms submitted along with form response details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()

        if not current_user_id:
            return jsonify({"error": "User not found"}), 403
        
        if not user or not user.authority:
            return jsonify({"error": "User does not have an authority"}), 403
        
        authority_id = str(user.authority.id)

        # current_user_role = request.headers.get('User-Role')
           
        result = ServiceRequestedService.get_all_requested_services(
            user_id=current_user_id,
            authority_id=authority_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving requested services: {str(e)}"
        }), 500

@service_requsted_bp.route('user/requested', methods=['GET'])
@jwt_required()
@role_required('Citizen')
def get_requested_services_by_user():
    """Get all services linked to forms submitted along with form response details"""
    try:
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return jsonify({"error": "User not found"}), 403
           
        result = ServiceRequestedService.get_all_requested_services_by_user(
            user_id=current_user_id,
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving requested services: {str(e)}"
        }), 500

@service_requsted_bp.route('/requested/count', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')   
def get_requested_services_count():
    """Get all services count linked to forms submitted along with form response details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()

        if not current_user_id:
            return jsonify({"error": "User not found"}), 403
        
        if not user or not user.authority:
            return jsonify({"error": "User does not have an authority"}), 403
        
        authority_id = str(user.authority.id)

        # current_user_role = request.headers.get('User-Role')
           
        result = ServiceRequestedService.get_all_requested_services(
            user_id=current_user_id,
            authority_id=authority_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving requested services: {str(e)}"
        }), 500
    

    
@service_requsted_bp.route('/peek', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')   
def get_peek_booking_hours():
    """Get peek booking hours"""
    try:
        # current_user_id = get_jwt_identity()
        # user = User.objects(id=current_user_id).first()

        # if not current_user_id:
        #     return jsonify({"error": "User not found"}), 403
        
        # if not user or not user.authority:
        #     return jsonify({"error": "User does not have an authority"}), 403
        
        # authority_id = str(user.authority.id)

        # current_user_role = request.headers.get('User-Role')
           
        result = ServiceRequestedService.get_peak_booking_hours()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving requested services: {str(e)}"
        }), 500