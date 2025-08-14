from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.service_service import ServiceService
from app.services.form_service import FormService
from app.models.respose import FormResponse
from app.utils.decorators import role_required

# Create Blueprint
service_bp = Blueprint('service', __name__, url_prefix='/service')

# Service CRUD endpoints
@service_bp.route('/create', methods=['POST'])
@jwt_required()
@role_required('GovAdmin')
def create_service():
    """
    Create a new service
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        service_service = ServiceService()
        service = service_service.create_service(data)
        return jsonify(service.to_dict()), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create service: {str(e)}"}), 500

@service_bp.route('/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_all_services():
    """
    Get all services with optional filtering
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        status_filter = request.args.get('status')
        
        service_service = ServiceService()
        services = service_service.get_all_services(skip=skip, limit=limit, status_filter=status_filter)
        
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch services: {str(e)}"}), 500
    

@service_bp.route('/services/<service_id>', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_service_by_id(service_id):
    """
    Get a specific service by ID
    """
    try:
        service_service = ServiceService()
        service = service_service.get_service_by_id(service_id)
        
        if not service:
            return jsonify({"error": "Service not found"}), 404
            
        return jsonify(service.to_dict()), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid service ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch service: {str(e)}"}), 500

@service_bp.route('/service/<service_id>', methods=['PUT'])
@jwt_required()
@role_required('GovAdmin')
def update_service(service_id):
    """
    Update an existing service
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        service_service = ServiceService()
        
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            return jsonify({"error": "Service not found"}), 404
        
        # Update service
        service = service_service.update_service(service_id, data)
        return jsonify(service.to_dict()), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid service ID format"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update service: {str(e)}"}), 500

@service_bp.route('/service/<service_id>', methods=['DELETE'])
@jwt_required()
@role_required('GovAdmin')
def delete_service(service_id):
    """
    Delete a service
    """
    try:
        service_service = ServiceService()
        
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            return jsonify({"error": "Service not found"}), 404
        
        service_service.delete_service(service_id)
        return jsonify({"message": "Service deleted successfully"}), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid service ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to delete service: {str(e)}"}), 500

@service_bp.route('/service/<service_id>/status', methods=['PATCH'])
@jwt_required()
@role_required('GovAdmin')
def update_service_status(service_id):
    """
    Update service status (Active/Inactive)
    """
    try:
        data = request.get_json()
        status_value = data.get('status')
        
        if not status_value or status_value not in ["Active", "Inactive"]:
            return jsonify({"error": "Status must be either 'Active' or 'Inactive'"}), 400
        
        service_service = ServiceService()
        
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            return jsonify({"error": "Service not found"}), 404
        
        service = service_service.update_service(service_id, {"status": status_value})
        return jsonify(service.to_dict()), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid service ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update service status: {str(e)}"}), 500

@service_bp.route('/services/search', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def search_services():
    """
    Search services by name or note
    """
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({"error": "Search term is required"}), 400
        
        service_service = ServiceService()
        services = service_service.search_services(search_term)
        
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to search services: {str(e)}"}), 500

@service_bp.route('/services/active', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_active_services():
    """
    Get all active services
    """
    try:
        service_service = ServiceService()
        services = service_service.get_active_services()
        
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch active services: {str(e)}"}), 500
    
@service_bp.route('/services/requested/<email>', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_requested_services_by_email(email):
    """Get all services linked to forms submitted by this email"""
    try:
        # Step 1: Find all form responses from this email
        form_responses = FormResponse.objects(respondent_email=email)

        if not form_responses:
            return jsonify({
                "success": False,
                "message": "No form submissions found for this email"
            }), 404

        services_list = []
        seen_service_ids = set()

        # Step 2: Loop through each response and get the service
        for fr in form_responses:
            form_id = str(fr.form.id) if hasattr(fr.form, "id") else str(fr.form)
            
            service_result = FormService.get_service_by_form_id(form_id)

            if service_result["success"]:
                service = service_result["service"]
                service_id = str(service["id"]) if isinstance(service, dict) else str(service.id)

                # Avoid duplicates
                if service_id not in seen_service_ids:
                    services_list.append(service)
                    seen_service_ids.add(service_id)

        return jsonify({
            "success": True,
            "services": services_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving requested services: {str(e)}"
        }), 500



# @service_bp.route('/media/<media_id>', methods=['GET'])
# def get_media_by_id(media_id):
#     """
#     Get media by ID
#     """
#     try:
#         media_service = MediaService()
#         media = media_service.get_media_by_id(media_id)
        
#         if not media:
#             return jsonify({"error": "Media not found"}), 404
            
#         return jsonify(media.to_dict()), 200
        
#     except InvalidId:
#         return jsonify({"error": "Invalid media ID format"}), 400
#     except Exception as e:
#         return jsonify({"error": f"Failed to fetch media: {str(e)}"}), 500

# @service_bp.route('/media', methods=['GET'])
# def get_all_media():
#     """
#     Get all media files
#     """
#     try:
#         skip = int(request.args.get('skip', 0))
#         limit = int(request.args.get('limit', 100))
        
#         media_service = MediaService()
#         media_files = media_service.get_all_media(skip=skip, limit=limit)
        
#         return jsonify([media.to_dict() for media in media_files]), 200
        
#     except Exception as e:
#         return jsonify({"error": f"Failed to fetch media files: {str(e)}"}), 500


@service_bp.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": "Bad request"}), 400

@service_bp.errorhandler(404)
def handle_not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@service_bp.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal server error"}), 500