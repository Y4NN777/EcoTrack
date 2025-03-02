from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from models import db, User, WasteType, Collection, Schedule, Report
from functools import wraps
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc
import csv
from io import StringIO
import os
import logging

reporting_bp = Blueprint('reporting', __name__)

def reporting_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_reporting_user():
            return jsonify({
                'status': 'error',
                'message': 'You do not have permission to access this page.',
                'redirect': url_for('index')
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@reporting_bp.route('/reporting/dashboard')
@login_required
@reporting_required
def dashboard():
    # Get counts and statistics for dashboard
    total_collections = Collection.query.count()
    total_waste_types = WasteType.query.count()
    total_schedules = Schedule.query.count()
    recent_reports = Report.query.order_by(Report.generated_at.desc()).limit(5).all()

    # Get waste collection by type
    waste_by_type = db.session.query(
        WasteType.name,
        func.sum(Collection.quantity).label('total_quantity')
    ).join(Collection).group_by(WasteType.name).all()

    return render_template('reporting/dashboard.html',
                         total_collections=total_collections,
                         total_waste_types=total_waste_types,
                         total_schedules=total_schedules,
                         recent_reports=recent_reports,
                         waste_by_type=waste_by_type)

@reporting_bp.route('/reporting/reports')
@login_required
@reporting_required
def reports():
    reports = Report.query.order_by(Report.generated_at.desc()).all()
    
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

    return render_template('reporting/reports.html',
                         reports=reports,
                         waste_by_type=waste_by_type,
                         collection_trends=collection_trends)



@reporting_bp.route('/reporting/export', methods=['POST'])
@login_required
@reporting_required
def export_data():
    try:
        # Get waste by type data for the last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        waste_by_type = db.session.query(
            WasteType.name,
            func.sum(Collection.quantity).label('total_quantity')
        ).join(Collection)\
         .filter(Collection.collection_date >= thirty_days_ago)\
         .group_by(WasteType.name)\
         .order_by(desc('total_quantity'))\
         .all()

        # Get daily collection trends for the last 30 days
        collection_trends = db.session.query(
            Collection.collection_date.label('date'),
            func.sum(Collection.quantity).label('total_quantity'),
            func.count(Collection.id).label('total_collections')
        ).filter(Collection.collection_date >= thirty_days_ago)\
         .group_by(Collection.collection_date)\
         .order_by(Collection.collection_date)\
         .all()

        # Get total statistics
        total_stats = db.session.query(
            func.count(Collection.id).label('total_collections'),
            func.sum(Collection.quantity).label('total_quantity')
        ).filter(Collection.collection_date >= thirty_days_ago).first()

        # Prepare CSV data
        rows = []
        
        # Add summary section
        rows.extend([
            ['Summary Statistics (Last 30 Days)'],
            ['Total Collections', str(total_stats.total_collections or 0)],
            ['Total Quantity (kg)', f"{total_stats.total_quantity or 0:.2f}"],
            [],  # Empty row for spacing
        ])

        # Add waste distribution section
        rows.extend([
            ['Waste Distribution by Type'],
            ['Waste Type', 'Total Quantity (kg)', 'Percentage of Total']
        ])
        
        if waste_by_type:
            total_waste = sum(wt.total_quantity or 0 for wt in waste_by_type)
            for waste_type in waste_by_type:
                percentage = (waste_type.total_quantity / total_waste * 100) if total_waste > 0 else 0
                rows.append([
                    waste_type.name,
                    f"{waste_type.total_quantity:.2f}",
                    f"{percentage:.1f}%"
                ])
        else:
            rows.append(['No waste data found', '', ''])
        
        rows.append([])  # Empty row for spacing

        # Add daily collection trends section
        rows.extend([
            ['Daily Collection Trends'],
            ['Date', 'Total Collections', 'Total Quantity (kg)', 'Average Quantity per Collection (kg)']
        ])
        
        if collection_trends:
            for trend in collection_trends:
                avg_quantity = (trend.total_quantity / trend.total_collections) if trend.total_collections > 0 else 0
                rows.append([
                    trend.date.strftime('%Y-%m-%d') if isinstance(trend.date, (datetime, date)) else trend.date,
                    str(trend.total_collections),
                    f"{trend.total_quantity:.2f}",
                    f"{avg_quantity:.2f}"
                ])
        else:
            rows.append(['No collection trends found', '', '', ''])

        # Create CSV file
        os.makedirs('instance/reports', exist_ok=True)
        filename = f'waste_management_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join('instance/reports', filename)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logging.error(f'Error exporting data: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Error exporting data. Please try again.'
        }), 500, {'Content-Type': 'application/json'}
