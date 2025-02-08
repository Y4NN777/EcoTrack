from flask import render_template, request, redirect, url_for, jsonify, flash, Response
from flask_login import login_required, current_user
from models import db, WasteType, Collection, Schedule
from blueprints.auth import admin_required, operator_required, reporting_required
from datetime import datetime, timedelta
import io
import csv

def init_routes(app):
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # Get dashboard statistics
        total_waste = db.session.query(db.func.sum(Collection.quantity)).scalar() or 0
        recycling_rate = calculate_recycling_rate()
        collections_today = Collection.query.filter(
            db.func.date(Collection.collection_date) == datetime.utcnow().date()
        ).count()
        active_routes = Schedule.query.filter(
            Schedule.pickup_date >= datetime.utcnow()
        ).distinct(Schedule.route).count()

        # Get upcoming collections (including scheduled ones)
        now = datetime.utcnow()
        upcoming_collections = []
        
        # Get immediate collections (within next hour)
        immediate_collections = Collection.query.filter(
            Collection.collection_date >= now,
            Collection.collection_date <= now + timedelta(hours=1)
        ).order_by(Collection.collection_date).all()
        
        # Get scheduled collections
        scheduled_collections = Schedule.query.filter(
            Schedule.pickup_date >= now,
            Schedule.status == 'Scheduled'
        ).order_by(Schedule.pickup_date).limit(5).all()
        
        # Combine and sort all upcoming collections
        for collection in immediate_collections:
            upcoming_collections.append({
                'date': collection.collection_date,
                'type': 'Collection',
                'waste_type': collection.waste_type,
                'location': collection.location,
                'status': collection.status
            })
            
        for schedule in scheduled_collections:
            upcoming_collections.append({
                'date': schedule.pickup_date,
                'type': 'Scheduled',
                'waste_type': schedule.waste_type,
                'location': schedule.route,
                'status': schedule.status
            })
            
        # Sort by date and limit to 5
        upcoming_collections.sort(key=lambda x: x['date'])
        upcoming_collections = upcoming_collections[:5]

        # Get recent activities
        recent_activities = get_recent_activities()

        return render_template('index.html',
                             total_waste=total_waste,
                             recycling_rate=recycling_rate,
                             collections_today=collections_today,
                             active_routes=active_routes,
                             upcoming_collections=upcoming_collections,
                             recent_activities=recent_activities)

    @app.route('/waste-types')
    @login_required
    @admin_required
    def waste_types():
        waste_types = WasteType.query.all()
        return render_template('admin/waste_types.html', waste_types=waste_types)

    @app.route('/waste-types/new', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def new_waste_type():
        if request.method == 'POST':
            waste_type = WasteType(
                name=request.form['name'],
                description=request.form['description'],
                disposal_method=request.form['disposal_method']
            )
            db.session.add(waste_type)
            db.session.commit()
            flash('Waste type added successfully!', 'success')
            return redirect(url_for('waste_types'))
        return render_template('admin/new_waste_type.html')

    @app.route('/collections')
    @login_required
    def collections():
        if current_user.is_admin():
            return redirect(url_for('admin.collections'))
            
        # For operators, show only their collections
        if current_user.is_operator():
            collections = Collection.query.filter_by(user_id=current_user.id)\
                .order_by(Collection.collection_date.desc()).all()
            waste_types = WasteType.query.all()
            return render_template('operator/collections.html', 
                             collections=collections,
                             waste_types=waste_types)
        # For reporting users, show all collections
        elif current_user.is_reporting_user():
            collections = Collection.query.order_by(Collection.collection_date.desc()).all()
            waste_types = WasteType.query.all()
            return render_template('reporting/collections.html', 
                             collections=collections,
                             waste_types=waste_types)
        else:
            flash('You do not have permission to view collections.', 'error')
            return redirect(url_for('index'))
            
    @app.route('/collections/new', methods=['GET', 'POST'])
    @login_required
    @operator_required
    def new_collection():
        if request.method == 'POST':
            try:
                collection = Collection(
                    user_id=current_user.id,
                    waste_type_id=request.form['waste_type_id'],
                    quantity=float(request.form['quantity']),
                    collection_date=datetime.strptime(request.form['collection_date'], '%Y-%m-%d'),
                    status='Pending',
                    location=request.form['location']
                )
                db.session.add(collection)
                db.session.commit()
                flash('Collection added successfully!', 'success')
                return redirect(url_for('collections'))
            except Exception as e:
                flash(f'Error adding collection: {str(e)}', 'error')
                return redirect(url_for('collections'))
                
        waste_types = WasteType.query.all()
        return render_template('operator/new_collection.html', waste_types=waste_types)

    @app.route('/schedules')
    @login_required
    def schedules():
        if current_user.is_admin():
            return redirect(url_for('admin.schedules'))
            
        # For operators and reporting users, show all schedules
        schedules = Schedule.query.order_by(Schedule.pickup_date).all()
        return render_template('operator/schedules.html', schedules=schedules)

    @app.route('/schedules/new', methods=['GET', 'POST'])
    @login_required
    @operator_required
    def new_schedule():
        if request.method == 'POST':
            try:
                schedule = Schedule(
                    user_id=current_user.id,
                    route=request.form['route'],
                    pickup_date=datetime.strptime(request.form['pickup_date'], '%Y-%m-%d'),
                    status='Scheduled'
                )
                db.session.add(schedule)
                db.session.commit()
                flash('Schedule added successfully!', 'success')
                return redirect(url_for('schedules'))
            except Exception as e:
                flash(f'Error adding schedule: {str(e)}', 'error')
                return redirect(url_for('schedules'))
                
        return render_template('operator/new_schedule.html')

    @app.route('/schedules/<int:id>/complete', methods=['POST'])
    @login_required
    @operator_required
    def complete_schedule(id):
        schedule = Schedule.query.get_or_404(id)
        schedule.is_completed = True
        db.session.commit()
        flash('Schedule marked as completed!', 'success')
        return redirect(url_for('schedules'))

    @app.route('/reports')
    @login_required
    @reporting_required
    def reports():
        waste_by_type = get_waste_by_type()
        collection_trends = get_collection_trends()
        return render_template('reporting/reports.html',
                             waste_by_type=waste_by_type,
                             collection_trends=collection_trends)

    @app.route('/export-report')
    @login_required
    @reporting_required
    def export_report():
        collections = Collection.query.order_by(Collection.collection_date.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Waste Type', 'Quantity (kg)', 'Location', 'Disposal Method'])
        
        # Write data
        for collection in collections:
            writer.writerow([
                collection.collection_date.strftime('%Y-%m-%d'),
                collection.waste_type.name,
                collection.quantity,
                collection.location,
                collection.disposal_method
            ])
        
        output.seek(0)
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=waste_collections_report.csv'}
        )

    @app.route('/api/export-csv')
    @login_required
    @reporting_required
    def export_csv():
        try:
            # Get all collections with waste type information
            collections = db.session.query(
                Collection.collection_date,
                WasteType.name.label('waste_type'),
                Collection.quantity,
                Collection.location,
                Collection.disposal_method
            ).join(WasteType).order_by(Collection.collection_date.desc()).all()

            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Waste Type', 'Quantity (kg)', 'Location', 'Disposal Method'])
            
            for collection in collections:
                writer.writerow([
                    collection.collection_date.strftime('%Y-%m-%d'),
                    collection.waste_type,
                    collection.quantity,
                    collection.location,
                    collection.disposal_method
                ])

            # Create the response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=waste_collections.csv'}
            )
        except Exception as e:
            flash(f'Error generating CSV: {str(e)}', 'error')
            return redirect(url_for('reports'))

    @app.route('/api/stats')
    @login_required
    @reporting_required
    def get_stats():
        today = datetime.utcnow().date()
        
        # Get collection stats
        total_collections = Collection.query.count()
        collections_today = Collection.query.filter(
            Collection.collection_date >= today
        ).count()
        
        # Get schedule stats
        total_schedules = Schedule.query.count()
        pending_schedules = Schedule.query.filter_by(is_completed=False).count()
        
        return jsonify({
            'total_collections': total_collections,
            'collections_today': collections_today,
            'total_schedules': total_schedules,
            'pending_schedules': pending_schedules
        })

    @app.route('/terms')
    def terms():
        """Display Terms of Service page."""
        return render_template('terms.html')

    @app.route('/privacy')
    def privacy():
        """Display Privacy Policy page."""
        return render_template('privacy.html')

def calculate_recycling_rate():
    """Calculate the overall recycling rate based on waste types and their disposal methods.
    
    The recycling rate is calculated as:
    (Recyclable + Compostable + Reusable Waste) / Total Waste * 100
    
    Returns:
        float: Percentage of waste that is recycled, composted, or reused
    """
    total_waste = db.session.query(db.func.sum(Collection.quantity)).scalar() or 0
    if total_waste == 0:
        return 0
    
    # Get waste that is recycled, composted, or reused
    sustainable_waste = db.session.query(db.func.sum(Collection.quantity))\
        .join(WasteType)\
        .filter(
            db.or_(
                WasteType.disposal_method.ilike('%recycle%'),
                WasteType.disposal_method.ilike('%compost%'),
                WasteType.disposal_method.ilike('%reuse%')
            )
        ).scalar() or 0
    
    return round((sustainable_waste / total_waste) * 100, 2)

def get_recent_activities():
    # Combine recent collections and schedules
    recent = []
    collections = Collection.query.order_by(Collection.created_at.desc()).limit(5).all()
    schedules = Schedule.query.order_by(Schedule.created_at.desc()).limit(5).all()
    
    for collection in collections:
        recent.append({
            'description': f'Collection of {collection.quantity}kg {collection.waste_type.name}',
            'time': collection.created_at
        })
    
    for schedule in schedules:
        recent.append({
            'description': f'New schedule created for {schedule.route}',
            'time': schedule.created_at
        })
    
    return sorted(recent, key=lambda x: x['time'], reverse=True)[:5]

def get_waste_by_type():
    try:
        results = db.session.query(
            WasteType.name,
            db.func.sum(Collection.quantity)
        ).join(Collection).group_by(WasteType.name).all()
        
        # Convert to list of tuples with proper type conversion
        return [(str(name), float(quantity) if quantity else 0) for name, quantity in results]
    except Exception as e:
        print(f"Error getting waste by type: {e}")
        return []

def get_collection_trends():
    try:
        # Get collection data for the last 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        results = db.session.query(
            db.func.date(Collection.collection_date),
            db.func.sum(Collection.quantity)
        ).filter(Collection.collection_date >= start_date)\
         .group_by(db.func.date(Collection.collection_date))\
         .order_by(db.func.date(Collection.collection_date)).all()
        
        # Convert to list of tuples with proper type conversion and date formatting
        return [(datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y-%m-%d'), 
                float(quantity) if quantity else 0) 
                for date, quantity in results]
    except Exception as e:
        print(f"Error getting collection trends: {e}")
        return []
