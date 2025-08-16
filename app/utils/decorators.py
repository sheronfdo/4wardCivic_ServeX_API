"""
Custom decorators for role-based access control
"""
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.services.user_service import UserService


def role_required(*allowed_roles):
    """Decorator to restrict access to specific roles"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user_service = UserService()
                user = user_service.get_user_by_id(current_user_id)

                if not user:
                    return jsonify({'error': 'User not found'}), 404

                if user.role not in allowed_roles:
                    return jsonify({'error': f'Access denied: Requires one of {allowed_roles} role'}), 403

                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify({'error': f'Access denied: {str(e)}'}), 403

        return decorated_function

    return decorator