"""
Configuration classes for different environments
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Database settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/serveX')
    MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'serveX')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # SMTP Setting
    MAILTRAP_HOST = os.environ.get('MAILTRAP_HOST', 'sandbox.smtp.mailtrap.io')
    MAILTRAP_PORT = os.environ.get('MAILTRAP_PORT', 2525)
    MAILTRAP_USERNAME = os.environ.get('MAILTRAP_USERNAME', 'c3b7e0d7963471')
    MAILTRAP_PASSWORD =  os.environ.get('MAILTRAP_PASSWORD', '4e311449eebefa')
    MAILTRAP_FROM_EMAIL =  os.environ.get('MAILTRAP_FROM_EMAIL', 'no-reply@servex.com')

    # MinIO settings
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'http://localhost:9000').strip()
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'servex')
    MINIO_SECURE = str(os.environ.get('MINIO_SECURE', 'False')).lower() in ('true', '1', 't')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'serveX_dev_db')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'serveX_prod_db')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'serveX_test_db')


def get_config(config_name):
    """Get configuration by name"""
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_mapping.get(config_name, DevelopmentConfig)