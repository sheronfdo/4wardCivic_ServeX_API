from flask import Blueprint, jsonify, request
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from app.models.dashboard import Dashboard
from app.services.dashbord_service import DashboardService
from app.models.user import User

dashboard_bp = Blueprint('dash', __name__, url_prefix='/dash')
dashboard_service = DashboardService()

@dashboard_bp.route('/total/services', methods=['GET'])
def get_total_services():
    """Get total services count"""
    try:
        total = dashboard_service.get_total_services_count()
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
def get_active_services():
    """Get active services count"""
    try:
        active = dashboard_service.get_active_services_count()
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
def get_pending_services():
    """Get pending services count"""
    try:
        pending = dashboard_service.get_pending_services_count()
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
def get_recent_services():
    """Get recent services count"""
    try:
        recent = dashboard_service.get_recent_services_count()
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
def get_chart_data():
    """Get monthly usage chart data"""
    try:
        chart_data = dashboard_service.get_monthly_chart_data()
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
def get_recent_activities():
    """Get recent activities"""
    try:
        limit = request.args.get('limit', 5, type=int)
        activities = dashboard_service.get_recent_activities(limit)
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
def get_dashboard_summary():
    """Get complete dashboard data in one call"""
    try:
        summary = dashboard_service.get_complete_dashboard_data()
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
def get_dashboard_statistics():
    """Get all key statistics"""
    try:
        stats = dashboard_service.get_key_statistics()
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