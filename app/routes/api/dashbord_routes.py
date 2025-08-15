from flask import Blueprint, jsonify, request
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from app.models.dashboard import Dashboard
from app.services.dashbord_service import DashboardService# Fixed import path
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required

dashboard_bp = Blueprint('dash', __name__, url_prefix='/dash')
dashboard_service = DashboardService()

def get_user_authority_id():
    """Helper function to get current user's authority ID"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user or not user.authority:
            return None
        
        return str(user.authority.id)
    except Exception as e:
        print(f"Error getting user authority: {e}")
        return None

@dashboard_bp.route('/total/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_total_services():
    """Get total services count filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        total = dashboard_service.get_total_services_count(authority_id)
        return jsonify({
            "success": True,
            "data": {
                "total_services": total
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/active/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_active_services():
    """Get active services count filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        active = dashboard_service.get_active_services_count(authority_id)
        return jsonify({
            "success": True,
            "data": {
                "active_services": active
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/pending/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_pending_services():
    """Get pending services count filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        pending = dashboard_service.get_pending_services_count(authority_id)
        return jsonify({
            "success": True,
            "data": {
                "pending_services": pending
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/recent/services', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_recent_services():
    """Get recent services count filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        recent = dashboard_service.get_recent_services_count(authority_id)
        return jsonify({
            "success": True,
            "data": {
                "recent_services": recent
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/chart/data', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_chart_data():
    """Get monthly usage chart data filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        chart_data = dashboard_service.get_monthly_chart_data(authority_id)
        return jsonify({
            "success": True,
            "data": chart_data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/activities', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_recent_activities():
    """Get recent activities filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        limit = request.args.get('limit', 5, type=int)
        activities = dashboard_service.get_recent_activities(limit, authority_id)
        return jsonify({
            "success": True,
            "data": {
                "activities": activities
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_dashboard_summary():
    """Get complete dashboard data in one call filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        summary = dashboard_service.get_complete_dashboard_data(authority_id)
        return jsonify({
            "success": True,
            "data": summary
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@dashboard_bp.route('/statistics', methods=['GET'])
@jwt_required()
@role_required('GovAdmin')
def get_dashboard_statistics():
    """Get all key statistics filtered by user's authority"""
    try:
        authority_id = get_user_authority_id()
        if not authority_id:
            return jsonify({
                "success": False,
                "message": "User does not have an authority"
            }), 403
        
        stats = dashboard_service.get_key_statistics(authority_id)
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@dashboard_bp.route('/profile/<id>', methods=['GET'])
# Mobile & GoVAdmin Api
@jwt_required()
@role_required('GovAdmin','Citizen')
def get_profile(id):
    """
    Get profile by ID
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(id):
            return jsonify({"error": "Invalid user ID"}), 400
        
        # Fetch the user
        user = User.objects.get(id=id)

        return jsonify({
            "success": True,
            "profile": user.to_dict()
        }), 200

    except DoesNotExist:
        return jsonify({"error": "User not found"}), 404

    except ValidationError:
        return jsonify({"error": "Invalid user ID format"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers for dashboard blueprint
@dashboard_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Dashboard endpoint not found"
    }), 404

@dashboard_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error in dashboard"
    }), 500