import os
from flask import Flask

app = Flask(__name__)

# Check for FLASK_ENV (deprecated) or FLASK_DEBUG
flask_env = os.environ.get('FLASK_ENV')
flask_debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')

if flask_env == 'production' or (not flask_debug and flask_env != 'development'):
    print("Using Production configuration")
    app.config.from_object('app.config.ProductionConfig')
else:
    app.config.from_object('app.config.DevelopmentConfig')
    # Setup the debug toolbar
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

# Setup the database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Setup Flask-Migrate for database migrations
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Setup caching
from flask_caching import Cache
cache = Cache(app)

# Setup APScheduler for background tasks
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

scheduler = BackgroundScheduler(timezone=app.config.get('SCHEDULER_TIMEZONE', 'US/Eastern'))
# Don't start scheduler here - let it be started explicitly via commands or when server runs
# scheduler.start()

# Register shutdown handler to stop scheduler on app exit
def shutdown_scheduler():
    """Shutdown scheduler when application exits."""
    if scheduler.running:
        scheduler.shutdown(wait=False)

atexit.register(shutdown_scheduler)

# Import the views
from app.views import main, error
