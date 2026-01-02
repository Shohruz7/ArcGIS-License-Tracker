import logging
import os


class BaseConfig(object):
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_size': 10,  # Connection pool size
        'max_overflow': 20,  # Max overflow connections
    }
    DEBUG_TB_ENABLED = False
    TIMEZONE = 'US/Eastern'
    LOG_LEVEL = logging.INFO
    LOG_FILENAME = 'activity.log'
    LOG_MAXBYTES = 20000
    LOG_BACKUPS = 0
    SECRET_KEY = os.getenv('SECRET_KEY', 'houdini')  # Use environment variable in production
    # Database URI - supports SQLite, SQL Server, PostgreSQL, MySQL
    # SQLite (default): sqlite:///app.db
    # SQL Server: mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
    # PostgreSQL: postgresql://user:password@server/database
    # MySQL: mysql+pymysql://user:password@server/database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    # Caching configuration
    CACHE_TYPE = 'SimpleCache'  # Use SimpleCache for development (in-memory)
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout
    CACHE_THRESHOLD = 1000  # Maximum number of items in cache


class DevelopmentConfig(BaseConfig):
    DEBUG_TB_ENABLED = True
    DEVELOPMENT = True
    DEBUG = True
    # Shorter cache timeout in development for easier testing
    CACHE_DEFAULT_TIMEOUT = 60  # 1 minute in development


class TestingConfig(BaseConfig):
    # use sqlite by default
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    # Longer cache timeout in production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes in production
    # For production, consider using Redis or Memcached
    # CACHE_TYPE = 'RedisCache'
    # CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    # SQL Server connection example:
    # SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server'
    # Or use environment variable: DATABASE_URL
