from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, WasteType, Collection, Schedule
from functools import wraps
from datetime import datetime, date, timedelta

operator_bp = Blueprint('operator', __name__)

def operator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_operator():
            return jsonify({
                'status': 'error',
                'message': 'You do not have permission to access this page.',
                'redirect': url_for('index')
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@operator_bp.route('/operator/dashboard')
@login_required
@operator_required
def dashboard():
    # Get counts for operator dashboard
    waste_type_count = WasteType.query.count()
    collections_today = Collection.query.filter(
        Collection.collection_date >= date.today()
    ).count()
    scheduled_pickups = Schedule.query.filter(
        Schedule.pickup_date >= date.today()
    ).count()

    return render_template('operator/dashboard.html',
                         waste_type_count=waste_type_count,
                         collections_today=collections_today,
                         scheduled_pickups=scheduled_pickups)

@operator_bp.route('/operator/collections')
@login_required
@operator_required
def collections():
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    waste_types = WasteType.query.all()
    return render_template('operator/collections.html', 
                         collections=collections,
                         waste_types=waste_types)

@operator_bp.route('/operator/collection/new', methods=['GET', 'POST'])
@login_required
@operator_required
def new_collection():
    if request.method == 'GET':
        waste_types = WasteType.query.all()
        return render_template('operator/new_collection.html', 
                             waste_types=waste_types,
                             today=date.today())

    try:
        # Parse the collection date
        collection_date = datetime.strptime(request.form.get('collection_date'), '%Y-%m-%dT%H:%M')
        
        # Only validate that collection date is not in the future
        if collection_date > datetime.now() + timedelta(hours=1):  # Allow 1 hour buffer
            return jsonify({
                'status': 'error',
                'message': 'Collection date cannot be in the future. Use Schedule feature for future collections.'
            }), 400

        # Create new collection
        collection = Collection(
            user_id=current_user.id,
            waste_type_id=request.form.get('waste_type_id'),
            quantity=float(request.form.get('quantity')),
            collection_date=collection_date,
            location=request.form.get('location'),
            status='Completed'  # Since this is a past collection, it's already completed
        )
        
        db.session.add(collection)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Collection logged successfully!',
            'redirect': url_for('operator.collections')
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format or quantity value'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error logging collection. Please try again.'
        }), 500

@operator_bp.route('/operator/collection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@operator_required
def edit_collection(id):
    collection = Collection.query.get_or_404(id)
    
    # Verify ownership
    if collection.user_id != current_user.id:
        flash('You do not have permission to edit this collection.', 'error')
        return redirect(url_for('operator.collections'))
    
    if request.method == 'GET':
        waste_types = WasteType.query.all()
        return render_template('operator/new_collection.html', 
                             collection=collection,
                             waste_types=waste_types)
    
    try:
        # Parse the collection date
        collection_date = datetime.strptime(request.form.get('collection_date'), '%Y-%m-%dT%H:%M')
        
        # Only validate that collection date is not in the future
        if collection_date > datetime.now() + timedelta(hours=1):  # Allow 1 hour buffer
            return jsonify({
                'status': 'error',
                'message': 'Collection date cannot be in the future. Use Schedule feature for future collections.'
            }), 400

        collection.waste_type_id = request.form.get('waste_type_id')
        collection.quantity = float(request.form.get('quantity'))
        collection.collection_date = collection_date
        collection.location = request.form.get('location')
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Collection updated successfully!',
            'redirect': url_for('operator.collections')
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format or quantity value'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating collection. Please try again.'
        }), 500

@operator_bp.route('/operator/collection/<int:id>/delete', methods=['POST'])
@login_required
@operator_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    
    # Check if the collection belongs to the current user
    if collection.user_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to delete this collection'
        }), 403
    
    try:
        db.session.delete(collection)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Collection deleted successfully!',
            'redirect': url_for('operator.collections')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error deleting collection. Please try again.'
        }), 500

@operator_bp.route('/operator/schedules')
@login_required
@operator_required
def schedules():
    # Show all schedules for operators
    schedules = Schedule.query.order_by(Schedule.pickup_date).all()
    return render_template('operator/schedules.html', schedules=schedules)

@operator_bp.route('/operator/schedule/new', methods=['GET', 'POST'])
@login_required
@operator_required
def new_schedule():
    if request.method == 'GET':
        waste_types = WasteType.query.all()
        return render_template('operator/new_schedule.html', 
                             waste_types=waste_types)

    try:
        # Parse and validate pickup date
        pickup_date = datetime.strptime(request.form.get('pickup_date'), '%Y-%m-%dT%H:%M')
        if pickup_date <= datetime.now():
            return jsonify({
                'status': 'error',
                'message': 'Pickup date must be in the future'
            }), 400

        # Create new schedule
        schedule = Schedule(
            waste_type_id=request.form.get('waste_type_id'),
            route=request.form.get('route'),
            pickup_date=pickup_date,
            team=request.form.get('team', 'Default Team'),
            status='Scheduled'
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Schedule created successfully!',
            'redirect': url_for('operator.schedules')
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error creating schedule. Please try again.'
        }), 500

@operator_bp.route('/operator/schedule/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@operator_required
def edit_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    
    if request.method == 'GET':
        waste_types = WasteType.query.all()
        return render_template('operator/new_schedule.html', 
                             schedule=schedule,
                             waste_types=waste_types)
    
    try:
        # Parse and validate pickup date
        pickup_date = datetime.strptime(request.form.get('pickup_date'), '%Y-%m-%dT%H:%M')
        if pickup_date <= datetime.now():
            return jsonify({
                'status': 'error',
                'message': 'Pickup date must be in the future'
            }), 400

        schedule.waste_type_id = request.form.get('waste_type_id')
        schedule.route = request.form.get('route')
        schedule.pickup_date = pickup_date
        schedule.team = request.form.get('team', schedule.team)
        schedule.status = request.form.get('status', schedule.status)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Schedule updated successfully!',
            'redirect': url_for('operator.schedules')
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating schedule. Please try again.'
        }), 500

@operator_bp.route('/operator/schedule/<int:id>/delete', methods=['POST'])
@login_required
@operator_required
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Schedule deleted successfully!',
            'redirect': url_for('operator.schedules')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error deleting schedule. Please try again.'
        }), 500
