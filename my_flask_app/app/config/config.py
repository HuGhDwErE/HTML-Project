import os
from datetime import timedelta

class BaseConfig:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    MAX_CONTENT_LENGTH = 1024 * 1024
    SECRET_KEY = os.getenv("SECRET_KEY")

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'

class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///production.db')


def get_config_by_name(config_name):
    """ Get config by name """
    if config_name == 'development':
        return DevelopmentConfig()
    elif config_name == 'production':
        return ProductionConfig()
    elif config_name == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
