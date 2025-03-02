"""
Waste Management System - Main Application
---------------------------------------
This is the main entry point for the Waste Management System web application.
It initializes the Flask application, sets up configurations, and registers blueprints.

The application follows a modular structure with different blueprints for:
- Authentication (auth_bp)
- Admin functionality (admin_bp)
- Operator functionality (operator_bp)
- Reporting functionality (reporting_bp)

Authors: GUISSOU Ali, DABO R Yanis Axel, OUEDRAOGO Yanis Aslane
Course: Python Programming II
Instructor: Mr Porgo
"""

from flask import Flask
from flask_migrate import Migrate
from models import db
from blueprints.auth import auth_bp, init_login_manager
from blueprints.admin import admin_bp
from blueprints.operator import operator_bp
from blueprints.reporting import reporting_bp
from routes import init_routes
import os

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask application instance configured with:
        - SQLite database
        - Login manager
        - Registered blueprints
        - Error handlers
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
    
    # Set database path in instance folder
    db_path = os.path.join(app.instance_path, 'wms.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'reports'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Create database tables
    with app.app_context():
        db.create_all()
        
    # Initialize login manager (after tables are created)
    init_login_manager(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(operator_bp)
    app.register_blueprint(reporting_bp)

    # Initialize routes
    init_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
