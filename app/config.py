import logging
import os


class BaseConfig(object):
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
    }
    DEBUG_TB_ENABLED = False
    TIMEZONE = 'US/Eastern'
    LOG_LEVEL = logging.INFO
    LOG_FILENAME = 'activity.log'
    LOG_MAXBYTES = 20000
    LOG_BACKUPS = 0
    SECRET_KEY = os.getenv('SECRET_KEY', 'houdini')  # Use environment variable in production
    # use sqlite by default
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')


class DevelopmentConfig(BaseConfig):
    DEBUG_TB_ENABLED = True
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(BaseConfig):
    # use sqlite by default
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True


class ProductionConfig(BaseConfig):
    DEBUG = False
