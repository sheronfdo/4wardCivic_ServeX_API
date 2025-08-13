from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from mongoengine import connect
import os
import boto3
from botocore.client import Config
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

    # Initialize MinIO client
    app.minio_client = boto3.client(
        's3',
        endpoint_url=app.config['MINIO_ENDPOINT'],
        aws_access_key_id=app.config['MINIO_ACCESS_KEY'],
        aws_secret_access_key=app.config['MINIO_SECRET_KEY'],
        config=Config(signature_version='s3v4')
    )

    # Create MinIO bucket if it doesn't exist
    try:
        app.minio_client.create_bucket(Bucket=app.config['MINIO_BUCKET'])
    except app.minio_client.exceptions.BucketAlreadyExists:
        pass
    except Exception as e:
        app.logger.error(f"Failed to create MinIO bucket: {str(e)}")

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
