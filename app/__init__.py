# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Add custom Jinja filters
    @app.template_filter('filter_nursing_unit')
    def filter_nursing_unit(nurse, unit_number):
        """Check if a unit number is in the nurse's NursingUnits string."""
        if nurse.NursingUnits:
            units = str(nurse.NursingUnits).split(',')
            return str(unit_number) in units
        return False
    
    return app
