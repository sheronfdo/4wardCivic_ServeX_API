from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.service_service import ServiceService
from app.services.form_service import FormService
from app.models.respose import FormResponse
from app.models.user import User
from app.utils.decorators import role_required
from bson.errors import InvalidId

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
        current_user_Id = get_jwt_identity()
        user = User.objects(id=current_user_Id).first()

        if not user or not user.authority:
            return jsonify({"error": "User does not have an authority"}), 403
        data = request.get_json()
        data["authority_id"] = str(user.authority.id)

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

# Mobile & GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen')
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


@service_bp.route('/Authority/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin','GovStaff')
def get_all_Authority_services():
    """
    Get all services for the logged-in user's authority (or by query authority_id)
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        status_filter = request.args.get('status')
        authority_id = request.args.get('authority_id')  # optional

        # Get current user
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # If no authority_id passed, default to user's authority
        if not authority_id:
            if not user.authority:
                return jsonify({"error": "User has no authority assigned"}), 403
            authority_id = str(user.authority.id)

        # Pass authority_id to service service
        service_service = ServiceService()
        services = service_service.get_all_authority_services(
            skip=skip,
            limit=limit,
            status_filter="Active",
            authority_id=authority_id
        )

        return jsonify([service.to_dict() for service in services]), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch services: {str(e)}"}), 500
    

@service_bp.route('/services/auth/<authority_id>', methods=['GET'])
@jwt_required()
@role_required('Citizen')
def get_all_services_by_id(authority_id):
    """
    Get all services for a given authority_id
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        status_filter = request.args.get('status')
        authority_id = authority_id

        if not authority_id:
            return jsonify({"error": "authority_id is required"}), 400

        service_service = ServiceService()
        services = service_service.get_all_authority_services(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            authority_id=authority_id
        )

        return jsonify([service.to_dict() for service in services]), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch services: {str(e)}"}), 500

@service_bp.route('/services/<service_id>', methods=['GET'])
#Mobile & GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen','GovStaff')
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

@service_bp.route('/services/<service_id>', methods=['DELETE'])
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
# Mobile API
@jwt_required()
@role_required('Citizen')
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
    
@service_bp.route('/services/requested/', methods=['GET'])
# Mobile API
@jwt_required()
@role_required('Citizen')
def get_requested_services_by_User():
    """Get all services linked to forms submitted by this user"""
    try:
        current_user_Id = get_jwt_identity()
        user = User.objects(id=current_user_Id).first()
        # Step 1: Find all form responses from this email
        form_responses = FormResponse.objects(user=user)

        if not form_responses:
            return jsonify({
                "success": False,
                "message": "No form submissions found for this user"
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

# @service_bp.route('/services/requested', methods=['GET'])
# # GovAdmin API
# @jwt_required()
# @role_required('GovAdmin')
# def get_requested_services():
#     """Get all services linked to forms submitted along with form response details"""
#     try:
#         form_responses = FormResponse.objects()

#         if not form_responses:
#             return jsonify({
#                 "success": False,
#                 "message": "No form submissions found"
#             }), 404

#         results = []
#         seen_service_ids = set()

#         for fr in form_responses:
#             # Get Service from Form
#             form_obj = fr.form
#             service_result = FormService.get_service_by_form_id(str(form_obj.id))
#             if not service_result["success"]:
#                 continue

#             service = service_result["service"]
#             service_id = str(service["id"]) if isinstance(service, dict) else str(service.id)

#             if service_id not in seen_service_ids:
#                 results.append({
#                     "service": service,
#                     "form_response": {
#                         "id": str(fr.id),
#                         "form_id": str(fr.form.id),
#                         "responses": fr.responses,
#                         # "respondent_email": fr.respondent_email,
#                         # "ip_address": fr.ip_address,
#                         # "user_agent": fr.user_agent,
#                         "submitted_at": fr.submitted_at.isoformat() if fr.submitted_at else None
#                     }
#                 })
#                 seen_service_ids.add(service_id)

#         return jsonify({
#             "success": True,
#             "data": results
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "message": f"Error retrieving requested services: {str(e)}"
#         }), 500

@service_bp.route('/service/avilibleslot', methods=['GET'])
# GovAdmin API
@jwt_required()
@role_required('GovAdmin','Citizen')
def get_available_slot():
    """Get all available slot details"""
    try:
        service_id = request.args.get("service_id")  # ✅ get from query param
        if not service_id:
            return jsonify({"error": "Missing service_id"}), 400

        service_service = ServiceService()
        services = service_service.get_available_slots(service_id, "2025-08-24", 5)
        return jsonify(services), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch active services: {str(e)}"}), 500



# def get_avilable_slot():
#     """Get all avilible slot details"""
#     try:
#         service_service = ServiceService()
#         data = request.get_json()
#         services = service_service.get_available_slots(data.get("service_id"),"2025-08-16",5)
        
#         return jsonify(services), 200
        
#     except Exception as e:
#         return jsonify({"error": f"Failed to fetch active services: {str(e)}"}), 500


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