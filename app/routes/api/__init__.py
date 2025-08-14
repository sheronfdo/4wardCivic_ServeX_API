"""
API routes package
"""
from flask import Blueprint
from app.routes.api.auth_routes import auth_bp
from app.routes.api.media_routes import media_bp
from app.routes.api.service_routes import service_bp
from app.routes.api.form_routes import form_bp
from app.routes.api.authority_routes import authority_bp
from app.routes.api.dashbord_routes import dashboard_bp
# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register sub-blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(media_bp, url_prefix='/media')
api_bp.register_blueprint(service_bp, url_prefix='/service')
api_bp.register_blueprint(form_bp, url_prefix='/form')
api_bp.register_blueprint(authority_bp, url_prefix='/authority')
api_bp.register_blueprint(dashboard_bp, url_prefix='/dash')

# Health check route
@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    from datetime import datetime
    from mongoengine import connection
    
    try:
        # Test database connection
        connection.get_db().command('ping')
        return {
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 500