from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId
from app.services.service_service import ServiceService
from app.services.media_service import MediaService
# Create Blueprint
service_bp = Blueprint('service', __name__, url_prefix='/service')



# Service CRUD endpoints
@service_bp.route('/create', methods=['POST'])
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

@service_bp.route('/service/<service_id>', methods=['GET'])
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