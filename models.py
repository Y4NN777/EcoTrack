"""
Waste Management System Database Models
------------------------------------
This module defines the database models for the Waste Management System.
It uses SQLAlchemy ORM to define tables and relationships.

Models:
- User: System users with different roles (Admin, Operator, Reporting)
- WasteType: Different types of waste that can be collected
- Collection: Records of waste collections
- Schedule: Future collection planning
- Report: Generated reports and analytics

Authors: GUISSOU Ali, DABO R Yanis Axel, OUEDRAOGO Yanis Aslane
Course: Python Programming II
Instructor: Mr Porgo
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class WasteType(db.Model):
    """Represents different types of waste that can be collected.
    
    Attributes:
        name: Name of the waste type
        description: Detailed description of the waste type
        disposal_method: Recommended method for disposing this type of waste
        collections: Relationship to collections of this waste type
    """
    __tablename__ = 'waste_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    disposal_method = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Collection(db.Model):
    """Records of actual waste collections performed by operators.
    
    Attributes:
        user_id: ID of the operator who performed the collection
        waste_type_id: Type of waste collected
        quantity: Amount of waste collected (in kg)
        collection_date: When the collection occurred
        location: Where the collection took place
        status: Current status of the collection
    """
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    waste_type_id = db.Column(db.Integer, db.ForeignKey('waste_types.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    collection_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('collections', lazy=True))
    waste_type = db.relationship('WasteType', backref=db.backref('collections', lazy=True))
    
    def __repr__(self):
        return f'<Collection {self.id}>'

class Schedule(db.Model):
    """Future collection planning and scheduling.
    
    Attributes:
        waste_type_id: Type of waste to be collected
        route: Collection route or area
        pickup_date: Planned collection date and time
        status: Current status (Scheduled, In Progress, Completed, Cancelled)
        team: Assigned collection team
    """
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    waste_type_id = db.Column(db.Integer, db.ForeignKey('waste_types.id'), nullable=False)
    route = db.Column(db.String(255), nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Scheduled')
    team = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    waste_type = db.relationship('WasteType', backref=db.backref('schedules', lazy=True))
    
    def __repr__(self):
        return f'<Schedule {self.id}>'

class User(UserMixin, db.Model):
    """System users with role-based access control.
    
    Roles:
        Administrator: Full system access
        Waste Management Operator: Collection and schedule management
        Reporting User: View and generate reports
    
    Attributes:
        username: Unique username for login
        email: User's email address
        password_hash: Securely hashed password
        role: User's role in the system
        collections: Relationship to collections performed by this user
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Securely hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == 'Administrator'

    def is_operator(self):
        """Check if user is a waste management operator."""
        return self.role == 'Waste Management Operator'

    def is_reporting(self):
        """Check if user has reporting role."""
        return self.role == 'Reporting'

    def is_reporting_user(self):
        """Check if user can access reports (includes admins)."""
        return self.role == 'Reporting User' or self.role == 'Administrator'

class Report(db.Model):
    """Generated reports and analytics.
    
    Attributes:
        type: Type of report (e.g., 'Collection Summary', 'Recycling Rate')
        period: Time period covered by the report
        format: Output format (e.g., 'PDF', 'CSV')
        status: Processing status
        file_path: Where the generated report is stored
    """
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    period = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Processing')
    file_path = db.Column(db.String(255))
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.type} {self.period}>'
