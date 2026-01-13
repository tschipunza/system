"""
Analytics and Reporting Routes
"""

from flask import Blueprint, render_template, request, jsonify, send_file, session, flash, redirect, url_for, g
from functools import wraps
import pymysql
from datetime import datetime, timedelta
import pandas as pd
import io
import os
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
from audit_logger import audit_logger
import time
from permission_manager import require_permission, permission_manager, get_permission_context

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('employee_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Get database connection for current tenant"""
    from app import get_db_connection as app_get_db
    return app_get_db()

@analytics_bp.context_processor
def inject_permissions():
    """Inject permission context into all analytics templates"""
    return get_permission_context()

# ===========================
# DASHBOARD & KPI CALCULATIONS
# ===========================

@analytics_bp.route('/dashboard')
@login_required
@require_permission('view_dashboard')
def dashboard():
    """Main analytics dashboard"""
    # Log dashboard access
    audit_logger.log_action('view_dashboard', 'dashboard')
    return render_template('analytics_dashboard.html')

@analytics_bp.route('/api/dashboard-stats')
@login_required
def get_dashboard_stats():
    """Get key statistics for dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Get user role and build data filter
        role_filter = ""
        filter_params = []
        
        if not permission_manager.has_permission('view_all_reports'):
            # Employee: filter to only their own records
            current_user_id = session.get('employee_id')
            role_filter = " AND employee_id = %s"
            filter_params = [current_user_id]
        
        # Total vehicles and status breakdown
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'in_use' THEN 1 ELSE 0 END) as in_use,
                SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
            FROM vehicles
        """)
        vehicle_stats = cursor.fetchone()
        stats['vehicles'] = vehicle_stats
        
        # Fuel statistics (last 30 days) - filtered by role
        fuel_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COALESCE(SUM(fuel_amount), 0) as total_liters,
                COALESCE(SUM(fuel_cost), 0) as total_cost,
                COALESCE(AVG(fuel_cost / fuel_amount), 0) as avg_price_per_liter
            FROM fuel_records
            WHERE DATE(fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            {role_filter if role_filter else ''}
        """
        cursor.execute(fuel_query, filter_params)
        fuel_stats = cursor.fetchone()
        stats['fuel'] = {
            'total_records': fuel_stats['total_records'],
            'total_liters': float(fuel_stats['total_liters'] or 0),
            'total_cost': float(fuel_stats['total_cost'] or 0),
            'avg_price_per_liter': float(fuel_stats['avg_price_per_liter'] or 0)
        }
        
        # Active assignments - filtered by role
        assignment_query = f"""
            SELECT COUNT(*) as active_assignments
            FROM vehicle_assignments
            WHERE status = 'active'
            {role_filter if role_filter else ''}
        """
        cursor.execute(assignment_query, filter_params)
        stats['active_assignments'] = cursor.fetchone()['active_assignments']
        
        # Maintenance statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_services,
                COALESCE(SUM(cost), 0) as total_cost,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM service_maintenance
            WHERE DATE(service_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        """)
        maintenance_stats = cursor.fetchone()
        stats['maintenance'] = {
            'total_services': maintenance_stats['total_services'],
            'total_cost': float(maintenance_stats['total_cost'] or 0),
            'pending': maintenance_stats['pending'],
            'completed': maintenance_stats['completed']
        }
        
        # Vehicle utilization (assignments per vehicle in last 30 days)
        cursor.execute("""
            SELECT 
                v.id, v.make, v.model, v.vehicle_number,
                COUNT(va.id) as assignment_count
            FROM vehicles v
            LEFT JOIN vehicle_assignments va ON v.id = va.vehicle_id 
                AND DATE(va.assignment_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY v.id, v.make, v.model, v.vehicle_number
            HAVING assignment_count > 0
            ORDER BY assignment_count DESC
            LIMIT 10
        """)
        stats['top_utilized'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(stats)
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/fuel-costs-chart')
@login_required
def get_fuel_costs_chart():
    """Get fuel costs data for chart (by vehicle, last 6 months)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                v.make, v.model, v.vehicle_number,
                DATE_FORMAT(fr.fuel_date, '%%Y-%%m') as month,
                SUM(fr.fuel_cost) as total_cost,
                SUM(fr.fuel_amount) as total_liters
            FROM fuel_records fr
            JOIN vehicles v ON fr.vehicle_id = v.id
            WHERE DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY v.id, v.make, v.model, v.vehicle_number, month
            ORDER BY month, total_cost DESC
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Transform data for Chart.js
        vehicles = {}
        months = set()
        
        for row in data:
            vehicle_key = f"{row['make']} {row['model']} ({row['vehicle_number']})"
            month = row['month']
            months.add(month)
            
            if vehicle_key not in vehicles:
                vehicles[vehicle_key] = {}
            
            vehicles[vehicle_key][month] = float(row['total_cost'])
        
        # Format for Chart.js
        months_sorted = sorted(list(months))
        datasets = []
        
        # Color palette for vehicles
        colors_palette = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]
        
        for idx, (vehicle, costs) in enumerate(vehicles.items()):
            dataset = {
                'label': vehicle,
                'data': [costs.get(month, 0) for month in months_sorted],
                'borderColor': colors_palette[idx % len(colors_palette)],
                'backgroundColor': colors_palette[idx % len(colors_palette)] + '33',
                'tension': 0.3
            }
            datasets.append(dataset)
        
        return jsonify({
            'labels': months_sorted,
            'datasets': datasets
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/vehicle-utilization')
@login_required
def get_vehicle_utilization():
    """Get vehicle utilization rates"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        period_days = int(request.args.get('days', 30))
        
        cursor.execute(f"""
            SELECT 
                v.id, v.make, v.model, v.vehicle_number,
                COUNT(DISTINCT DATE(va.assignment_date)) as days_used,
                COUNT(va.id) as total_assignments,
                ROUND((COUNT(DISTINCT DATE(va.assignment_date)) / %s) * 100, 2) as utilization_rate
            FROM vehicles v
            LEFT JOIN vehicle_assignments va ON v.id = va.vehicle_id 
                AND DATE(va.assignment_date) >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY v.id, v.make, v.model, v.vehicle_number
            ORDER BY utilization_rate DESC
        """, (period_days, period_days))
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format for bar chart
        labels = [f"{row['make']} {row['model']}" for row in data]
        utilization_data = [float(row['utilization_rate']) for row in data]
        assignments_data = [row['total_assignments'] for row in data]
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Utilization Rate (%)',
                    'data': utilization_data,
                    'backgroundColor': '#36A2EB',
                    'yAxisID': 'y'
                },
                {
                    'label': 'Total Assignments',
                    'data': assignments_data,
                    'backgroundColor': '#FF6384',
                    'yAxisID': 'y1'
                }
            ]
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/maintenance-schedule')
@login_required
def get_maintenance_schedule():
    """Get upcoming maintenance schedule"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                v.make, v.model, v.vehicle_number,
                sm.service_type, sm.next_service_date as scheduled_date, sm.status, sm.cost,
                sm.description
            FROM service_maintenance sm
            JOIN vehicles v ON sm.vehicle_id = v.id
            WHERE sm.next_service_date >= CURDATE()
            ORDER BY sm.next_service_date ASC
            LIMIT 20
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format dates for JSON
        for row in data:
            if row['scheduled_date']:
                row['scheduled_date'] = row['scheduled_date'].strftime('%Y-%m-%d')
            row['cost'] = float(row['cost']) if row['cost'] else 0
        
        return jsonify(data)
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/fuel-efficiency-trends')
@login_required
def get_fuel_efficiency_trends():
    """Calculate fuel efficiency (km/liter) trends"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                v.make, v.model, v.vehicle_number,
                DATE_FORMAT(fr.fuel_date, '%%Y-%%m') as month,
                AVG(
                    CASE 
                        WHEN fr.odometer_reading IS NOT NULL AND fr.fuel_amount > 0 THEN
                            (fr.odometer_reading - LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fuel_date)) / fr.fuel_amount
                        ELSE NULL
                    END
                ) as avg_efficiency
            FROM fuel_records fr
            JOIN vehicles v ON fr.vehicle_id = v.id
            WHERE DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY v.id, v.make, v.model, v.vehicle_number, month
            HAVING avg_efficiency IS NOT NULL AND avg_efficiency > 0 AND avg_efficiency < 50
            ORDER BY month
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Group by vehicle
        vehicles = {}
        months = set()
        
        for row in data:
            vehicle_key = f"{row['make']} {row['model']}"
            month = row['month']
            months.add(month)
            
            if vehicle_key not in vehicles:
                vehicles[vehicle_key] = {}
            
            vehicles[vehicle_key][month] = round(float(row['avg_efficiency'] or 0), 2)
        
        months_sorted = sorted(list(months))
        datasets = []
        
        colors_palette = ['#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56', '#9966FF']
        
        for idx, (vehicle, efficiency) in enumerate(vehicles.items()):
            dataset = {
                'label': vehicle,
                'data': [efficiency.get(month, None) for month in months_sorted],
                'borderColor': colors_palette[idx % len(colors_palette)],
                'tension': 0.3,
                'fill': False
            }
            datasets.append(dataset)
        
        return jsonify({
            'labels': months_sorted,
            'datasets': datasets
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# ===========================
# CUSTOM REPORT BUILDER
# ===========================

@analytics_bp.route('/report-builder')
@login_required
def report_builder():
    """Custom report builder interface"""
    audit_logger.log_action('view_report', 'report_builder')
    return render_template('report_builder.html')

@analytics_bp.route('/api/generate-custom-report', methods=['POST'])
@login_required
def generate_custom_report():
    """Generate custom report based on user filters"""
    start_time = time.time()
    data = request.get_json()
    
    report_type = data.get('report_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    vehicle_ids = data.get('vehicle_ids', [])
    employee_ids = data.get('employee_ids', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if report_type == 'fuel_analysis':
            query = """
                SELECT 
                    fr.fuel_date,
                    v.make, v.model, v.vehicle_number,
                    e.username as filled_by,
                    fr.fuel_amount, fr.fuel_cost,
                    ROUND(fr.fuel_cost / fr.fuel_amount, 2) as price_per_liter,
                    fr.odometer_reading,
                    fr.station_name as location
                FROM fuel_records fr
                JOIN vehicles v ON fr.vehicle_id = v.id
                LEFT JOIN employees e ON fr.employee_id = e.id
                WHERE DATE(fr.fuel_date) BETWEEN %s AND %s
            """
            params = [start_date, end_date]
            
            if vehicle_ids:
                placeholders = ','.join(['%s'] * len(vehicle_ids))
                query += f" AND fr.vehicle_id IN ({placeholders})"
                params.extend(vehicle_ids)
            
            if employee_ids:
                placeholders = ','.join(['%s'] * len(employee_ids))
                query += f" AND fr.employee_id IN ({placeholders})"
                params.extend(employee_ids)
            
            query += " ORDER BY fr.fuel_date DESC"
            
        elif report_type == 'maintenance_costs':
            query = """
                SELECT 
                    sm.service_date as scheduled_date, sm.service_date as completion_date,
                    v.make, v.model, v.vehicle_number,
                    sm.service_type, sm.description,
                    sm.cost, sm.status,
                    sm.performed_by
                FROM service_maintenance sm
                JOIN vehicles v ON sm.vehicle_id = v.id
                WHERE DATE(sm.service_date) BETWEEN %s AND %s
            """
            params = [start_date, end_date]
            
            if vehicle_ids:
                placeholders = ','.join(['%s'] * len(vehicle_ids))
                query += f" AND sm.vehicle_id IN ({placeholders})"
                params.extend(vehicle_ids)
            
            query += " ORDER BY sm.service_date DESC"
            
        elif report_type == 'vehicle_assignments':
            query = """
                SELECT 
                    va.assignment_date, va.return_date,
                    v.make, v.model, v.vehicle_number,
                    e.username as assigned_to,
                    ea.username as assigned_by,
                    va.purpose, va.status,
                    va.mileage_at_assignment, va.mileage_at_return,
                    (va.mileage_at_return - va.mileage_at_assignment) as distance_traveled
                FROM vehicle_assignments va
                JOIN vehicles v ON va.vehicle_id = v.id
                JOIN employees e ON va.employee_id = e.id
                LEFT JOIN employees ea ON va.assigned_by = ea.id
                WHERE DATE(va.assignment_date) BETWEEN %s AND %s
            """
            params = [start_date, end_date]
            
            if vehicle_ids:
                placeholders = ','.join(['%s'] * len(vehicle_ids))
                query += f" AND va.vehicle_id IN ({placeholders})"
                params.extend(vehicle_ids)
            
            if employee_ids:
                placeholders = ','.join(['%s'] * len(employee_ids))
                query += f" AND va.employee_id IN ({placeholders})"
                params.extend(employee_ids)
            
            query += " ORDER BY va.assignment_date DESC"
        
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert datetime objects to strings
        for row in results:
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, (float, int)) and value is not None:
                    row[key] = float(value)
        
        cursor.close()
        conn.close()
        
        # Log report generation
        execution_time = int((time.time() - start_time) * 1000)
        audit_logger.log_action(
            'view_report',
            'custom_report',
            details={'report_type': report_type, 'rows': len(results)},
            execution_time_ms=execution_time
        )
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# ===========================
# EXPORT FUNCTIONS
# ===========================

@analytics_bp.route('/api/export-excel', methods=['POST'])
@login_required
@require_permission('export_excel')
def export_to_excel():
    """Export report data to Excel with formatting"""
    start_time = time.time()
    data = request.get_json()
    report_data = data.get('data', [])
    report_title = data.get('title', 'Fleet Manager Report')
    
    if not report_data:
        return jsonify({'error': 'No data to export'}), 400
    
    try:
        # Create pandas DataFrame
        df = pd.DataFrame(report_data)
        
        # Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write data
            df.to_excel(writer, sheet_name='Report', index=False, startrow=4)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Report']
            
            # Add title
            worksheet['A1'] = report_title
            worksheet['A1'].font = workbook.create_font(size=16, bold=True)
            
            # Add generation date
            worksheet['A2'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            
            # Get tenant name from session
            tenant_name = session.get('tenant_name', 'Fleet Manager')
            worksheet['A3'] = f'Company: {tenant_name}'
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Log export action
        execution_time = int((time.time() - start_time) * 1000)
        audit_logger.log_action(
            'export_excel',
            'custom_report',
            details={'title': report_title, 'rows': len(report_data)},
            execution_time_ms=execution_time
        )
        
        # Return file
        filename = f"{report_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/export-pdf', methods=['POST'])
@login_required
@require_permission('export_pdf')
def export_to_pdf():
    """Export report data to PDF with company branding"""
    start_time = time.time()
    data = request.get_json()
    report_data = data.get('data', [])
    report_title = data.get('title', 'Fleet Manager Report')
    
    if not report_data:
        return jsonify({'error': 'No data to export'}), 400
    
    try:
        # Create PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Add title
        tenant_name = session.get('tenant_name', 'Fleet Manager')
        elements.append(Paragraph(f"{tenant_name}", title_style))
        elements.append(Paragraph(report_title, styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Add metadata
        meta_data = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(meta_data, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Prepare table data
        if report_data:
            # Get headers
            headers = list(report_data[0].keys())
            table_data = [headers]
            
            # Add rows (limit to reasonable size)
            for row in report_data[:100]:  # Limit to 100 rows for PDF
                table_data.append([str(row.get(h, '')) for h in headers])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
            
            if len(report_data) > 100:
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Note: Showing first 100 of {len(report_data)} records", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        output.seek(0)
        
        # Log export action
        execution_time = int((time.time() - start_time) * 1000)
        audit_logger.log_action(
            'export_pdf',
            'custom_report',
            details={'title': report_title, 'rows': len(report_data)},
            execution_time_ms=execution_time
        )
        
        # Return file
        filename = f"{report_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===========================
# KPI TRACKING
# ===========================

@analytics_bp.route('/kpis')
@login_required
@require_permission('view_kpis')
def kpis_page():
    """KPI tracking dashboard"""
    audit_logger.log_action('view_report', 'kpis')
    return render_template('kpis.html')

@analytics_bp.route('/api/calculate-kpis')
@login_required
def calculate_kpis():
    """Calculate current KPIs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        kpis = {}
        
        # Cost per km (last 30 days)
        cursor.execute("""
            SELECT 
                COALESCE(SUM(fr.fuel_cost), 0) as total_fuel_cost,
                COALESCE(SUM(sm.cost), 0) as total_maintenance_cost,
                COALESCE(SUM(va.mileage_at_return - va.mileage_at_assignment), 0) as total_km
            FROM fuel_records fr
            LEFT JOIN service_maintenance sm ON DATE(sm.service_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            LEFT JOIN vehicle_assignments va ON DATE(va.assignment_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            WHERE DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        cost_data = cursor.fetchone()
        total_cost = float(cost_data['total_fuel_cost'] or 0) + float(cost_data['total_maintenance_cost'] or 0)
        total_km = float(cost_data['total_km'] or 0)
        kpis['cost_per_km'] = round(total_cost / total_km, 2) if total_km > 0 else 0
        
        # Average fuel efficiency
        cursor.execute("""
            SELECT AVG(efficiency) as avg_efficiency
            FROM (
                SELECT 
                    (fr.odometer_reading - LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fuel_date)) / fr.fuel_amount as efficiency
                FROM fuel_records fr
                WHERE fr.fuel_amount > 0
                    AND DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
            ) as efficiencies
            WHERE efficiency > 0 AND efficiency < 50
        """)
        eff_data = cursor.fetchone()
        kpis['avg_fuel_efficiency'] = round(float(eff_data['avg_efficiency'] or 0), 2)
        
        # Vehicle downtime (vehicles in maintenance)
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT v.id) as vehicles_down,
                (SELECT COUNT(*) FROM vehicles) as total_vehicles
            FROM vehicles v
            JOIN service_maintenance sm ON v.id = sm.vehicle_id
            WHERE sm.status IN ('pending', 'in_progress')
        """)
        downtime_data = cursor.fetchone()
        kpis['vehicle_downtime_pct'] = round(
            (downtime_data['vehicles_down'] / downtime_data['total_vehicles'] * 100) 
            if downtime_data['total_vehicles'] > 0 else 0, 2
        )
        
        # Fleet utilization rate
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT vehicle_id) as vehicles_used,
                (SELECT COUNT(*) FROM vehicles WHERE status != 'inactive') as active_vehicles
            FROM vehicle_assignments
            WHERE DATE(assignment_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        util_data = cursor.fetchone()
        kpis['utilization_rate'] = round(
            (util_data['vehicles_used'] / util_data['active_vehicles'] * 100)
            if util_data['active_vehicles'] > 0 else 0, 2
        )
        
        cursor.close()
        conn.close()
        
        return jsonify(kpis)
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500


# ===========================
# SCHEDULED REPORTS MANAGEMENT
# ===========================

@analytics_bp.route('/scheduled-reports')
@login_required
def scheduled_reports_list():
    """List all scheduled reports"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT sr.*, e.username as created_by_name,
                   (SELECT COUNT(*) FROM report_execution_log WHERE scheduled_report_id = sr.id) as execution_count
            FROM scheduled_reports sr
            JOIN employees e ON sr.created_by = e.id
            ORDER BY sr.created_at DESC
        """)
        reports = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('scheduled_reports.html', reports=reports)
        
    except Exception as e:
        cursor.close()
        conn.close()
        flash(f'Error loading scheduled reports: {str(e)}', 'danger')
        return redirect(url_for('analytics.dashboard'))


@analytics_bp.route('/scheduled-reports/create', methods=['GET', 'POST'])
@login_required
@require_permission('create_scheduled_reports')
def create_scheduled_report():
    """Create a new scheduled report"""
    if request.method == 'POST':
        report_name = request.form.get('report_name')
        report_type = request.form.get('report_type')
        frequency = request.form.get('frequency')
        recipients = request.form.get('recipients')
        report_format = request.form.get('report_format', 'excel')
        vehicle_ids = request.form.getlist('vehicle_ids')
        employee_ids = request.form.getlist('employee_ids')
        
        if not all([report_name, report_type, frequency, recipients]):
            flash('All required fields must be filled!', 'danger')
            return redirect(url_for('analytics.create_scheduled_report'))
        
        # Build filters JSON
        filters = {}
        if vehicle_ids:
            filters['vehicle_ids'] = vehicle_ids
        if employee_ids:
            filters['employee_ids'] = employee_ids
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Calculate next run date
            from scheduler import scheduled_reports_manager
            next_run = scheduled_reports_manager.calculate_next_run(frequency)
            
            cursor.execute("""
                INSERT INTO scheduled_reports 
                (report_name, report_type, frequency, recipients, report_format, filters, created_by, next_run_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (report_name, report_type, frequency, recipients, report_format, 
                  json.dumps(filters), session['employee_id'], next_run))
            
            report_id = cursor.lastrowid
            conn.commit()
            
            # Schedule the report
            cursor.execute("""
                SELECT sr.*, e.email as employee_email, e.username
                FROM scheduled_reports sr
                JOIN employees e ON sr.created_by = e.id
                WHERE sr.id = %s
            """, (report_id,))
            new_report = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # Add to scheduler
            scheduled_reports_manager.schedule_report(new_report)
            
            # Log report creation
            audit_logger.log_action(
                'create_scheduled_report',
                'scheduled_report',
                resource_id=report_id,
                details={'report_name': report_name, 'report_type': report_type, 'frequency': frequency}
            )
            
            flash(f'Scheduled report "{report_name}" created successfully!', 'success')
            return redirect(url_for('analytics.scheduled_reports_list'))
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f'Error creating scheduled report: {str(e)}', 'danger')
            return redirect(url_for('analytics.create_scheduled_report'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, vehicle_number, make, model FROM vehicles ORDER BY vehicle_number")
        vehicles = cursor.fetchall()
        
        cursor.execute("SELECT id, username, email FROM employees ORDER BY username")
        employees = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('create_scheduled_report.html', vehicles=vehicles, employees=employees)
        
    except Exception as e:
        cursor.close()
        conn.close()
        flash(f'Error loading form: {str(e)}', 'danger')
        return redirect(url_for('analytics.scheduled_reports_list'))


@analytics_bp.route('/scheduled-reports/<int:report_id>/toggle', methods=['POST'])
@login_required
def toggle_scheduled_report(report_id):
    """Enable/disable a scheduled report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT is_active FROM scheduled_reports WHERE id = %s", (report_id,))
        report = cursor.fetchone()
        
        if not report:
            flash('Report not found!', 'danger')
            return redirect(url_for('analytics.scheduled_reports_list'))
        
        new_status = not report['is_active']
        cursor.execute("UPDATE scheduled_reports SET is_active = %s WHERE id = %s", (new_status, report_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        status_text = 'enabled' if new_status else 'disabled'
        flash(f'Scheduled report {status_text} successfully!', 'success')
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f'Error toggling report: {str(e)}', 'danger')
    
    return redirect(url_for('analytics.scheduled_reports_list'))


@analytics_bp.route('/scheduled-reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_scheduled_report(report_id):
    """Delete a scheduled report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM scheduled_reports WHERE id = %s", (report_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Remove from scheduler
        from scheduler import scheduled_reports_manager
        job_id = f"report_{report_id}"
        if scheduled_reports_manager.scheduler.get_job(job_id):
            scheduled_reports_manager.scheduler.remove_job(job_id)
        
        # Log deletion
        audit_logger.log_action(
            'delete_scheduled_report',
            'scheduled_report',
            resource_id=report_id
        )
        
        flash('Scheduled report deleted successfully!', 'success')
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f'Error deleting report: {str(e)}', 'danger')
    
    return redirect(url_for('analytics.scheduled_reports_list'))


@analytics_bp.route('/scheduled-reports/<int:report_id>/run-now', methods=['POST'])
@login_required
def run_scheduled_report_now(report_id):
    """Execute a scheduled report immediately"""
    start_time = time.time()
    from scheduler import scheduled_reports_manager
    
    try:
        scheduled_reports_manager.execute_scheduled_report(report_id)
        
        # Log execution
        execution_time = int((time.time() - start_time) * 1000)
        audit_logger.log_action(
            'run_scheduled_report',
            'scheduled_report',
            resource_id=report_id,
            execution_time_ms=execution_time
        )
        
        flash('Report executed successfully! Check your email.', 'success')
    except Exception as e:
        flash(f'Error executing report: {str(e)}', 'danger')
    
    return redirect(url_for('analytics.scheduled_reports_list'))


@analytics_bp.route('/scheduled-reports/<int:report_id>/history')
@login_required
def scheduled_report_history(report_id):
    """View execution history for a scheduled report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get report details
        cursor.execute("""
            SELECT sr.*, e.username as created_by_name
            FROM scheduled_reports sr
            JOIN employees e ON sr.created_by = e.id
            WHERE sr.id = %s
        """, (report_id,))
        report = cursor.fetchone()
        
        if not report:
            flash('Report not found!', 'danger')
            return redirect(url_for('analytics.scheduled_reports_list'))
        
        # Get execution history
        cursor.execute("""
            SELECT * FROM report_execution_log
            WHERE scheduled_report_id = %s
            ORDER BY execution_date DESC
            LIMIT 50
        """, (report_id,))
        history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('scheduled_report_history.html', report=report, history=history)
        
    except Exception as e:
        cursor.close()
        conn.close()
        flash(f'Error loading history: {str(e)}', 'danger')
        return redirect(url_for('analytics.scheduled_reports_list'))


# ===========================
# AUDIT TRAIL
# ===========================

@analytics_bp.route('/audit-trail')
@login_required
@require_permission('view_audit_trail')
def audit_trail():
    """Audit trail viewing page (admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all employees for filter dropdown
        cursor.execute("SELECT id, username, email FROM employees ORDER BY username")
        employees = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('audit_trail.html', employees=employees)
        
    except Exception as e:
        cursor.close()
        conn.close()
        flash(f'Error loading audit trail: {str(e)}', 'danger')
        return redirect(url_for('analytics.dashboard'))


@analytics_bp.route('/api/audit-log')
@login_required
def get_audit_log():
    """Get paginated audit log with filters"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_type = request.args.get('action_type')
    employee_id = request.args.get('employee_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build query with filters
        where_clauses = []
        params = []
        
        if start_date:
            where_clauses.append("DATE(al.created_at) >= %s")
            params.append(start_date)
        
        if end_date:
            where_clauses.append("DATE(al.created_at) <= %s")
            params.append(end_date)
        
        if action_type:
            where_clauses.append("al.action_type = %s")
            params.append(action_type)
        
        if employee_id:
            where_clauses.append("al.employee_id = %s")
            params.append(employee_id)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM analytics_audit_log al
            WHERE 1=1 {where_sql}
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Get paginated logs
        offset = (page - 1) * page_size
        logs_query = f"""
            SELECT 
                al.*,
                e.username,
                e.email
            FROM analytics_audit_log al
            JOIN employees e ON al.employee_id = e.id
            WHERE 1=1 {where_sql}
            ORDER BY al.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(logs_query, params + [page_size, offset])
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/api/audit-summary')
@login_required
def get_audit_summary():
    """Get audit trail summary statistics"""
    days = int(request.args.get('days', 30))
    
    try:
        summary = audit_logger.get_analytics_summary(days)
        return jsonify({
            'success': True,
            'total_actions': summary['total_actions'],
            'unique_users': summary['unique_users'],
            'avg_execution_time': summary['avg_execution_time'],
            'today_actions': summary.get('today_actions', 0),
            'by_action_type': summary['by_action_type']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/api/audit-log/export')
@login_required
def export_audit_log():
    """Export audit log to Excel"""
    start_time = time.time()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_type = request.args.get('action_type')
    employee_id = request.args.get('employee_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build query with filters
        where_clauses = []
        params = []
        
        if start_date:
            where_clauses.append("DATE(al.created_at) >= %s")
            params.append(start_date)
        
        if end_date:
            where_clauses.append("DATE(al.created_at) <= %s")
            params.append(end_date)
        
        if action_type:
            where_clauses.append("al.action_type = %s")
            params.append(action_type)
        
        if employee_id:
            where_clauses.append("al.employee_id = %s")
            params.append(employee_id)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get all logs
        query = f"""
            SELECT 
                al.created_at as 'Timestamp',
                e.username as 'Employee',
                e.email as 'Email',
                al.action_type as 'Action',
                al.resource_type as 'Resource Type',
                al.resource_id as 'Resource ID',
                al.details as 'Details',
                al.execution_time_ms as 'Execution Time (ms)',
                al.ip_address as 'IP Address',
                al.user_agent as 'User Agent'
            FROM analytics_audit_log al
            JOIN employees e ON al.employee_id = e.id
            WHERE 1=1 {where_sql}
            ORDER BY al.created_at DESC
        """
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to DataFrame
        df = pd.DataFrame(logs)
        
        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Audit Log')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Audit Log']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        
        # Log export
        execution_time = int((time.time() - start_time) * 1000)
        audit_logger.log_action(
            'export_excel',
            'audit_log',
            details={'rows': len(logs), 'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'action_type': action_type,
                'employee_id': employee_id
            }},
            execution_time_ms=execution_time
        )
        
        filename = f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500
