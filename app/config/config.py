"""
Configuration classes for different environments
"""
import os
from datetime import timedelta


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