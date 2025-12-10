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

# Import the views
from app.views import main, error
