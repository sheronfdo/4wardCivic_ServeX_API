from flask import Blueprint, request, jsonify
from app.services.form_service import FormService
from app.models.service import Service
from app.models.form import Form
import re
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required

# Create blueprint for form routes
form_bp = Blueprint('form', __name__, url_prefix='/form')

def validate_object_id(id_string):
    """Validate if string is a valid MongoDB ObjectId"""
    return re.match(r'^[0-9a-fA-F]{24}$', id_string) is not None

def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

@form_bp.route('/create', methods=['POST'])
@jwt_required()
@role_required('GovAdmin')
def create_form():
    """Create a new form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get user ID from headers (you might want to implement JWT authentication)
        created_by = request.headers.get('X-User-ID')  # or get from JWT token
        
        result = FormService.create_form(data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@form_bp.route('/forms/<service_id>', methods=['GET'])
# Mobile & GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen','GovStaff')
def get_forms_by_service(service_id):
    """Get all forms for a specific service"""
    try:
        # Validate ObjectId
        if not validate_object_id(service_id):
            return jsonify({
                'success': False,
                'message': 'Invalid service ID format'
            }), 400

        # Check if service exists
        service = Service.objects(id=service_id).first()
        if not service:
            return jsonify({
                'success': False,
                'message': 'Service not found'
            }), 404

        # Get forms linked to this service
        forms = Form.objects(service=service)

        return jsonify({
            'success': True,
            'count': len(forms),
            'forms': [form.to_dict() for form in forms]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@form_bp.route('/<form_id>', methods=['GET'])
# Mobile & GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen')
def get_form(form_id):
    """Get a specific form by ID"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        result = FormService.get_form_by_id(form_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>', methods=['PUT'])
@jwt_required()
@role_required('GovAdmin')
def update_form(form_id):
    """Update a specific form"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get user ID from headers (implement proper authentication)
        updated_by = request.headers.get('X-User-ID')
        
        result = FormService.update_form(form_id, data, updated_by)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>', methods=['DELETE'])
@jwt_required()
@role_required('GovAdmin')
def delete_form(form_id):
    """Delete a specific form (soft delete)"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        # Get user ID from headers (implement proper authentication)
        deleted_by = request.headers.get('X-User-ID')
        
        result = FormService.delete_form(form_id, deleted_by)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/user/<user_id>', methods=['GET'])
# Mobile & GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen')
def get_user_forms(user_id):
    """Get all forms created by a user"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Limit the maximum number of results per page
        if limit > 100:
            limit = 100
        
        result = FormService.get_user_forms(user_id, page, limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>/submit', methods=['POST'])
#Mobile API
@jwt_required()
@role_required('Citizen','GovAdmin')
def submit_form_response(form_id):
    """Submit a response to a form"""
    try:
        user_Id = get_jwt_identity()
        if not user_Id :
            return jsonify({"error": "User Not Found "}), 403
        
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        data = request.get_json()
        data["user_id"] = str(user_Id)

        if not data:
            return jsonify({
                'success': False,
                'message': 'No response data provided'
            }), 400
        data = request.get_json()
        
        # Extract response data and metadata
        response_data = data.get('responses', {})
        
        result = FormService.submit_form_response(
            form_id, 
            user_Id,
            response_data, 
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>/responses', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_form_responses(form_id):
    """Get all responses for a form"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Limit the maximum number of results per page
        if limit > 100:
            limit = 100
        
        # Get user ID for access control (implement proper authentication)
        created_by = request.headers.get('X-User-ID')
        
        result = FormService.get_form_responses(form_id, page, limit, created_by)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>/analytics', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_form_analytics(form_id):
    """Get analytics for a form"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        # Get user ID for access control (implement proper authentication)
        created_by = request.headers.get('X-User-ID')
        
        result = FormService.get_form_analytics(form_id, created_by)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>/duplicate', methods=['POST'])
@jwt_required()
@role_required('GovAdmin')
def duplicate_form(form_id):
    """Duplicate an existing form"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        # Get the original form
        original_form_result = FormService.get_form_by_id(form_id)
        
        if not original_form_result['success']:
            return jsonify(original_form_result), 404
        
        original_form = original_form_result['form']
        
        # Create duplicate form data
        duplicate_data = {
            'title': f"{original_form['title']} (Copy)",
            'description': original_form['description'],
            'questions': original_form['questions']
        }
        
        # Get user ID from headers
        created_by = request.headers.get('X-User-ID')
        
        result = FormService.create_form(duplicate_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@form_bp.route('/<form_id>/export', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def export_form_data(form_id):
    """Export form and its responses as JSON"""
    try:
        # Validate ObjectId format
        if not validate_object_id(form_id):
            return jsonify({
                'success': False,
                'message': 'Invalid form ID format'
            }), 400
        
        # Get user ID for access control
        created_by = request.headers.get('X-User-ID')
        
        # Get form data
        form_result = FormService.get_form_by_id(form_id)
        if not form_result['success']:
            return jsonify(form_result), 404
        
        # Get form responses (all of them for export)
        responses_result = FormService.get_form_responses(form_id, page=1, limit=10000, created_by=created_by)
        
        export_data = {
            'form': form_result['form'],
            'responses': responses_result.get('responses', []) if responses_result['success'] else [],
            'export_date': FormService.datetime.utcnow().isoformat(),
            'total_responses': len(responses_result.get('responses', [])) if responses_result['success'] else 0
        }
        
        return jsonify({
            'success': True,
            'export_data': export_data
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

# Error handlers for the blueprint
@form_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request'
    }), 400

@form_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@form_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500
