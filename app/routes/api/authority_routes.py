from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId
from app.services.service_service import ServiceService
from app.services.media_service import MediaService
from app.services.authority_service import AuthorityService
from app.models.authority import Authority
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required

# Create Blueprint
authority_bp = Blueprint('authority', __name__, url_prefix='/authority')

# Mobile API
@authority_bp.route('/authorities', methods=['GET'])
@jwt_required()
@role_required('Citizen')
def get_all_authorities():
    """
    Get all authorities
    """
    try:
        status_filter = request.args.get('status')
        authority_service = AuthorityService()
        
        # Fetch all authorities with optional status filtering
        authorities = authority_service.get_all(status_filter=status_filter)
        
        # Convert each authority to dict for JSON response
        return jsonify([authority.to_dict() for authority in authorities]), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch authorities: {str(e)}"}), 500
  

@authority_bp.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": "Bad request"}), 400

@authority_bp.errorhandler(404)
def handle_not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@authority_bp.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal server error"}), 500