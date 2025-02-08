from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from models import db, User, WasteType, Collection, Schedule, Report
from functools import wraps
from datetime import datetime, date, timedelta
from sqlalchemy import func
import csv
from io import StringIO
import os
import logging
import re  # Added back for input validation

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'You do not have permission to access this page.',
                'redirect': url_for('index')
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    """Validate password meets requirements."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_email(email):
    """Validate email format."""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        return False, "Invalid email format"
    return True, "Email is valid"

def validate_username(username):
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

def validate_name(name, field_name):
    """Validate name format."""
    if len(name) < 2:
        return False, f"{field_name} must be at least 2 characters long"
    if not re.match(r'^[a-zA-Z\s-]+$', name):
        return False, f"{field_name} can only contain letters, spaces, and hyphens"
    return True, "Name is valid"

def validate_role(role):
    """Validate role."""
    valid_roles = ['Administrator', 'Waste Management Operator', 'Reporting User']
    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    return True, "Role is valid"

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    user_count = User.query.count()
    waste_type_count = WasteType.query.count()
    collections_today = Collection.query.filter(
        Collection.collection_date >= date.today()
    ).count()
    scheduled_pickups = Schedule.query.filter(
        Schedule.pickup_date >= date.today()
    ).count()

    return render_template('admin/dashboard.html',
                         user_count=user_count,
                         waste_type_count=waste_type_count,
                         collections_today=collections_today,
                         scheduled_pickups=scheduled_pickups)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/waste-types')
@login_required
@admin_required
def waste_types():
    waste_types = WasteType.query.all()
    return render_template('admin/waste_types.html', waste_types=waste_types)

@admin_bp.route('/admin/collections')
@login_required
@admin_required
def collections():
    collections = Collection.query.all()
    waste_types = WasteType.query.all()
    users = User.query.filter(User.role != 'Administrator').all()  # Get all non-admin users
    return render_template('admin/collections.html', 
                         collections=collections,
                         waste_types=waste_types,
                         users=users)

@admin_bp.route('/admin/schedules')
@login_required
@admin_required
def schedules():
    schedules = Schedule.query.all()
    return render_template('admin/schedules.html', schedules=schedules)

# CRUD operations for waste types
@admin_bp.route('/admin/waste-types/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_waste_type():
    if request.method == 'GET':
        return render_template('admin/new_waste_type.html')
        
    try:
        waste_type = WasteType(
            name=request.form.get('name'),
            description=request.form.get('description'),
            disposal_method=request.form.get('disposal_method')
        )
        db.session.add(waste_type)
        db.session.commit()
        flash('Waste type created successfully!', 'success')
        return redirect(url_for('admin.waste_types'))
    except Exception as e:
        db.session.rollback()
        flash('Error creating waste type. Please try again.', 'error')
        return redirect(url_for('admin.waste_types'))

@admin_bp.route('/admin/waste-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_waste_type(id):
    waste_type = WasteType.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('admin/new_waste_type.html', waste_type=waste_type)
        
    try:
        waste_type.name = request.form.get('name')
        waste_type.description = request.form.get('description')
        waste_type.disposal_method = request.form.get('disposal_method')
        db.session.commit()
        flash('Waste type updated successfully!', 'success')
        return redirect(url_for('admin.waste_types'))
    except Exception as e:
        db.session.rollback()
        flash('Error updating waste type. Please try again.', 'error')
        return redirect(url_for('admin.waste_types'))

@admin_bp.route('/admin/waste-types/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_waste_type(id):
    waste_type = WasteType.query.get_or_404(id)
    
    # Check for existing collections
    existing_collections = Collection.query.filter_by(waste_type_id=id).first()
    if existing_collections:
        return jsonify({
            'status': 'error',
            'message': 'Cannot delete this waste type because it has associated collections. Please delete the collections first or reassign them to a different waste type.'
        }), 400
        
    # Check for existing schedules
    existing_schedules = Schedule.query.filter_by(waste_type_id=id).first()
    if existing_schedules:
        return jsonify({
            'status': 'error',
            'message': 'Cannot delete this waste type because it has associated schedules. Please delete the schedules first or reassign them to a different waste type.'
        }), 400

    try:
        db.session.delete(waste_type)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Waste type deleted successfully!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error deleting waste type. Please try again.'
        }), 500

# Collection CRUD operations
@admin_bp.route('/admin/collections/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_collection():
    waste_types = WasteType.query.all()
    users = User.query.filter(User.role != 'Administrator').all()
    
    if request.method == 'GET':
        return render_template('admin/new_collection.html', 
                             waste_types=waste_types,
                             users=users,
                             collection=None,
                             today=date.today())
                             
    try:
        # Get date and time from form
        collection_date = request.form.get('collection_date')
        collection_time = request.form.get('collection_time', '00:00')
        collection_datetime = datetime.strptime(f"{collection_date} {collection_time}", '%Y-%m-%d %H:%M')
        
        # Validate collection datetime
        now = datetime.now()
        max_future = now + timedelta(hours=1)
        
        if collection_datetime > max_future:
            flash('Collections can only be logged up to 1 hour in the future. For later collections, please use the Schedules feature.', 'error')
            return render_template('admin/new_collection.html',
                                 waste_types=waste_types,
                                 users=users,
                                 collection=None,
                                 form_data=request.form)

        collection = Collection(
            user_id=request.form.get('user_id'),
            waste_type_id=request.form.get('waste_type_id'),
            quantity=float(request.form.get('quantity')),
            collection_date=collection_datetime,
            status=request.form.get('status', 'Pending'),
            location=request.form.get('location')
        )
        db.session.add(collection)
        db.session.commit()
        flash('Collection added successfully!', 'success')
        return redirect(url_for('admin.collections'))
    except ValueError as e:
        flash('Invalid date or time format. Please check your input.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding collection: {str(e)}', 'error')
    
    # Return to form with entered data on error
    return render_template('admin/new_collection.html',
                         waste_types=waste_types,
                         users=users,
                         collection=None,
                         form_data=request.form)

@admin_bp.route('/admin/collections/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_collection(id):
    collection = Collection.query.get_or_404(id)
    waste_types = WasteType.query.all()
    users = User.query.filter(User.role != 'Administrator').all()
    
    if request.method == 'GET':
        return render_template('admin/new_collection.html', 
                             collection=collection,
                             waste_types=waste_types,
                             users=users,
                             today=date.today())
                             
    try:
        # Get date and time from form
        collection_date = request.form.get('collection_date')
        collection_time = request.form.get('collection_time', '00:00')
        collection_datetime = datetime.strptime(f"{collection_date} {collection_time}", '%Y-%m-%d %H:%M')
        
        # Validate collection datetime
        now = datetime.now()
        max_future = now + timedelta(hours=1)
        
        if collection_datetime > max_future:
            flash('Collections can only be logged up to 1 hour in the future. For later collections, please use the Schedules feature.', 'error')
            return render_template('admin/new_collection.html',
                                 collection=collection,
                                 waste_types=waste_types,
                                 users=users,
                                 form_data=request.form)

        collection.user_id = request.form.get('user_id')
        collection.waste_type_id = request.form.get('waste_type_id')
        collection.quantity = float(request.form.get('quantity'))
        collection.collection_date = collection_datetime
        collection.status = request.form.get('status')
        collection.location = request.form.get('location')
        db.session.commit()
        flash('Collection updated successfully!', 'success')
        return redirect(url_for('admin.collections'))
    except ValueError as e:
        flash('Invalid date or time format. Please check your input.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating collection: {str(e)}', 'error')
    
    return render_template('admin/new_collection.html',
                         collection=collection,
                         waste_types=waste_types,
                         users=users,
                         form_data=request.form)

@admin_bp.route('/admin/collections/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    try:
        db.session.delete(collection)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Collection deleted successfully!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error deleting collection. Please try again.'
        }), 500

# Schedule CRUD operations
@admin_bp.route('/admin/schedules/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_schedule():
    waste_types = WasteType.query.all()
    if request.method == 'GET':
        return render_template('admin/new_schedule.html', 
                             waste_types=waste_types,
                             schedule=None,
                             today=date.today())
    try:
        # Get date and time from form
        pickup_date = request.form.get('pickup_date')
        pickup_time = request.form.get('pickup_time', '09:00')
        pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", '%Y-%m-%d %H:%M')
        
        # Validate pickup datetime is in the future
        if pickup_datetime <= datetime.now():
            flash('Schedule date and time must be in the future.', 'error')
            return render_template('admin/new_schedule.html',
                                 waste_types=waste_types,
                                 schedule=None,
                                 form_data=request.form)

        schedule = Schedule(
            waste_type_id=request.form.get('waste_type_id'),
            route=request.form.get('route'),
            pickup_date=pickup_datetime,
            status=request.form.get('status', 'Scheduled'),
            team=request.form.get('team')
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('admin.schedules'))
    except ValueError as e:
        flash('Invalid date or time format. Please check your input.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating schedule: {str(e)}', 'error')
    
    return render_template('admin/new_schedule.html',
                         waste_types=waste_types,
                         schedule=None,
                         form_data=request.form)

@admin_bp.route('/admin/schedules/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    waste_types = WasteType.query.all()
    
    if request.method == 'GET':
        return render_template('admin/new_schedule.html', 
                             schedule=schedule,
                             waste_types=waste_types,
                             today=date.today())
    try:
        # Get date and time from form
        pickup_date = request.form.get('pickup_date')
        pickup_time = request.form.get('pickup_time', '09:00')
        pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", '%Y-%m-%d %H:%M')
        
        # Validate pickup datetime is in the future
        if pickup_datetime <= datetime.now():
            flash('Schedule date and time must be in the future.', 'error')
            return render_template('admin/new_schedule.html',
                                 schedule=schedule,
                                 waste_types=waste_types,
                                 form_data=request.form)

        schedule.waste_type_id = request.form.get('waste_type_id')
        schedule.route = request.form.get('route')
        schedule.pickup_date = pickup_datetime
        schedule.status = request.form.get('status')
        schedule.team = request.form.get('team')
        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('admin.schedules'))
    except ValueError as e:
        flash('Invalid date or time format. Please check your input.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating schedule: {str(e)}', 'error')
    
    return render_template('admin/new_schedule.html',
                         schedule=schedule,
                         waste_types=waste_types,
                         form_data=request.form)

@admin_bp.route('/admin/schedules/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Schedule deleted successfully!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error deleting schedule. Please try again.'
        }), 500

# User management routes
@admin_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        db.session.begin_nested()
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            role = request.form.get('role', '').strip()

            if not all([username, email, password, first_name, last_name, role]):
                missing_fields = [field for field, value in {
                    'username': username,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role
                }.items() if not value]
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            validations = [
                validate_username(username),
                validate_email(email),
                validate_password(password),
                validate_name(first_name, "First name"),
                validate_name(last_name, "Last name"),
                validate_role(role)
            ]

            for is_valid, message in validations:
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': message
                    }), 400

            if User.query.filter_by(username=username).first():
                return jsonify({
                    'success': False,
                    'message': f'Username "{username}" is already taken'
                }), 400

            if User.query.filter_by(email=email).first():
                return jsonify({
                    'success': False,
                    'message': f'Email "{email}" is already registered'
                }), 400

            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True
            )
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'User {username} has been created successfully'
                }), 200
            except Exception as e:
                db.session.rollback()
                logging.error(f'Database error creating user: {str(e)}')
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred. Please try again.'
                }), 500

        except Exception as e:
            db.session.rollback()
            logging.error(f'Error creating user: {str(e)}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    return render_template('admin/user_form.html', user=None)

@admin_bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        db.session.begin_nested()
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            role = request.form.get('role', '').strip()
            is_active = request.form.get('is_active') == 'on'

            if not all([username, email, first_name, last_name, role]):
                missing_fields = [field for field, value in {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role
                }.items() if not value]
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            validations = [
                validate_username(username),
                validate_email(email),
                validate_name(first_name, "First name"),
                validate_name(last_name, "Last name"),
                validate_role(role)
            ]

            for is_valid, message in validations:
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': message
                    }), 400

            username_exists = User.query.filter(
                User.username == username,
                User.id != id
            ).first()
            if username_exists:
                return jsonify({
                    'success': False,
                    'message': f'Username "{username}" is already taken'
                }), 400

            email_exists = User.query.filter(
                User.email == email,
                User.id != id
            ).first()
            if email_exists:
                return jsonify({
                    'success': False,
                    'message': f'Email "{email}" is already registered'
                }), 400

            if password:
                is_valid, message = validate_password(password)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': message
                    }), 400

            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.is_active = is_active

            if password:
                user.set_password(password)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'User {username} has been updated successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error updating user: {str(e)}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    return render_template('admin/user_form.html', user=user)

@admin_bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    try:
        user = User.query.get_or_404(id)
        
        # Prevent deleting admin user
        if user.username == 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete admin user'
            }), 400
            
        # Check if user has related collections
        if user.collections:
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete user with existing collections'
            }), 400
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error deleting user: {str(e)}'
        }), 500

# Reports management routes
@admin_bp.route('/admin/reports')
@login_required
@admin_required
def reports():
    # Get counts and statistics
    total_collections = Collection.query.count()
    total_waste_kg = db.session.query(func.sum(Collection.quantity)).scalar() or 0
    active_users = User.query.filter_by(is_active=True).count()
    
    # Calculate completion rate
    total_schedules = Schedule.query.count()
    completed_collections = Collection.query.filter(Collection.status == 'Completed').count()
    completion_rate = round((completed_collections / total_schedules * 100) if total_schedules > 0 else 0, 1)
    
    # Get waste by type data for chart
    waste_by_type = db.session.query(
        WasteType.name,
        func.sum(Collection.quantity).label('total_quantity')
    ).join(Collection).group_by(WasteType.name).all()

    # Get collection trends for the last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    collection_trends = db.session.query(
        func.date(Collection.collection_date).label('date'),
        func.sum(Collection.quantity).label('total_quantity')
    ).filter(Collection.collection_date >= thirty_days_ago)\
     .group_by(func.date(Collection.collection_date))\
     .order_by(func.date(Collection.collection_date))\
     .all()

    return render_template('admin/reports.html',
                         total_collections=total_collections,
                         total_waste_kg=f"{total_waste_kg:.2f}",
                         active_users=active_users,
                         completion_rate=completion_rate,
                         waste_by_type=waste_by_type,
                         collection_trends=collection_trends)

@admin_bp.route('/admin/reports/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(id):
    try:
        report = Report.query.get_or_404(id)
        
        # Delete the file if it exists
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Report deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error deleting report: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Error deleting report. Please try again.'
        }), 500

@admin_bp.route('/admin/reports/<int:id>/download')
@login_required
@admin_required
def download_report(id):
    try:
        report = Report.query.get_or_404(id)
        
        if not report.file_path or not os.path.exists(report.file_path):
            return jsonify({
                'status': 'error',
                'message': 'Report file not found'
            }), 404
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=os.path.basename(report.file_path),
            mimetype='text/csv'
        )
    except Exception as e:
        logging.error(f'Error downloading report: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Error downloading report. Please try again.'
        }), 500
