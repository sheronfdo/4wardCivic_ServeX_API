"""
Flask app factory pattern implementation
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from mongoengine import connect
import os

from app.config.config import get_config
from app.routes.api import api_bp
from app.services.user_service import UserService


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)
    
    # Initialize database
    connect(
        db=app.config['MONGO_DATABASE'],
        host=app.config['MONGO_URI']
    )
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    register_error_handlers(app)
    
    # Create admin user on startup
    # with app.app_context():
    #     create_admin_user()
    
    return app


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'message': 'Bad request'}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'message': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'message': 'Forbidden'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'message': 'Internal server error'}, 500


# def create_admin_user():
#     """Create default admin user if it doesn't exist"""
#     try:
#         user_service = UserService()
#         admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        
#         if not user_service.find_by_email(admin_email):
#             admin_data = {
#                 'name': os.getenv('ADMIN_NAME', 'System Administrator'),
#                 'email': admin_email,
#                 'password': os.getenv('ADMIN_PASSWORD', 'admin123'),
#                 'role': 'Admin'
#             }
#             user_service.create_user(admin_data)
#             print(f"Admin user created: {admin_email}")
#     except Exception as e:
#         print(f"Error creating admin user: {e}")