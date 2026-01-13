"""
Scheduled Reports Background Job Scheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pymysql
from email_service import email_service
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json

class ScheduledReportsManager:
    """Manages scheduled report generation and email delivery"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.jobs_loaded = False
        
    def init_app(self, app):
        """Initialize with Flask app context"""
        self.app = app
        if not self.scheduler.running:
            self.scheduler.start()
            print("✓ Background scheduler started")
        
    def get_db_connection(self, database_name=None):
        """Get database connection"""
        if self.app:
            with self.app.app_context():
                from app import get_db_connection
                return get_db_connection()
        else:
            # Fallback for testing
            from config import TENANT_DATABASES
            db_config = TENANT_DATABASES.get(database_name) if database_name else TENANT_DATABASES['fleet_twt']
            return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    
    def load_scheduled_reports(self):
        """Load all active scheduled reports and create jobs"""
        if self.jobs_loaded:
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sr.*, e.email as employee_email, e.username
                FROM scheduled_reports sr
                JOIN employees e ON sr.created_by = e.id
                WHERE sr.is_active = TRUE
            """)
            
            reports = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for report in reports:
                self.schedule_report(report)
            
            self.jobs_loaded = True
            print(f"✓ Loaded {len(reports)} scheduled reports")
            
        except Exception as e:
            print(f"✗ Error loading scheduled reports: {e}")
    
    def schedule_report(self, report):
        """Schedule a single report"""
        job_id = f"report_{report['id']}"
        
        # Remove existing job if present
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Create cron trigger based on frequency
        if report['frequency'] == 'daily':
            trigger = CronTrigger(hour=8, minute=0)  # 8:00 AM daily
        elif report['frequency'] == 'weekly':
            trigger = CronTrigger(day_of_week='mon', hour=8, minute=0)  # Monday 8:00 AM
        elif report['frequency'] == 'monthly':
            trigger = CronTrigger(day=1, hour=8, minute=0)  # 1st of month, 8:00 AM
        else:
            print(f"⚠️  Unknown frequency: {report['frequency']}")
            return
        
        # Schedule the job
        self.scheduler.add_job(
            func=self.execute_scheduled_report,
            trigger=trigger,
            args=[report['id']],
            id=job_id,
            name=f"{report['report_name']} ({report['frequency']})",
            replace_existing=True
        )
        
        print(f"✓ Scheduled: {report['report_name']} ({report['frequency']})")
    
    def execute_scheduled_report(self, report_id):
        """Execute a scheduled report and send via email"""
        print(f"\n{'='*60}")
        print(f"Executing scheduled report ID: {report_id}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get report details
            cursor.execute("""
                SELECT sr.*, e.email as creator_email, e.username as creator_name
                FROM scheduled_reports sr
                JOIN employees e ON sr.created_by = e.id
                WHERE sr.id = %s
            """, (report_id,))
            
            report = cursor.fetchone()
            
            if not report:
                print(f"✗ Report {report_id} not found")
                return
            
            # Parse filters
            filters = json.loads(report['filters']) if report['filters'] else {}
            
            # Calculate date range based on frequency
            end_date = datetime.now().date()
            if report['frequency'] == 'daily':
                start_date = end_date - timedelta(days=1)
            elif report['frequency'] == 'weekly':
                start_date = end_date - timedelta(days=7)
            elif report['frequency'] == 'monthly':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Generate report data
            report_data = self.generate_report_data(
                cursor,
                report['report_type'],
                start_date,
                end_date,
                filters
            )
            
            if not report_data:
                print(f"⚠️  No data for report {report['report_name']}")
                self.log_execution(cursor, report_id, 'completed', 0, "No data available")
                conn.commit()
                cursor.close()
                conn.close()
                return
            
            # Generate file based on format
            if report['report_format'] == 'excel':
                file_data = self.generate_excel_report(report, report_data, start_date, end_date)
            else:  # pdf
                file_data = self.generate_pdf_report(report, report_data, start_date, end_date)
            
            # Send email to recipients
            recipients = report['recipients'].split(',')
            success = email_service.send_report_email(
                recipients,
                report['report_name'],
                file_data,
                report['report_format']
            )
            
            # Log execution
            status = 'completed' if success else 'failed'
            error_message = None if success else 'Email delivery failed'
            self.log_execution(cursor, report_id, status, len(report_data), error_message)
            
            # Update next_run_date
            next_run = self.calculate_next_run(report['frequency'])
            cursor.execute("""
                UPDATE scheduled_reports 
                SET next_run_date = %s, last_run_date = NOW()
                WHERE id = %s
            """, (next_run, report_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Report executed successfully: {report['report_name']}")
            print(f"  Recipients: {report['recipients']}")
            print(f"  Records: {len(report_data)}")
            print(f"  Next run: {next_run}")
            
        except Exception as e:
            print(f"✗ Error executing report {report_id}: {e}")
            try:
                self.log_execution(cursor, report_id, 'failed', 0, str(e))
                conn.commit()
            except:
                pass
    
    def generate_report_data(self, cursor, report_type, start_date, end_date, filters):
        """Generate report data based on type and filters"""
        vehicle_ids = filters.get('vehicle_ids', [])
        employee_ids = filters.get('employee_ids', [])
        
        if report_type == 'fuel_analysis':
            query = """
                SELECT 
                    fr.fuel_date,
                    v.vehicle_number,
                    CONCAT(v.make, ' ', v.model) as vehicle,
                    e.username as filled_by,
                    fr.fuel_amount,
                    fr.fuel_cost,
                    ROUND(fr.fuel_cost / fr.fuel_amount, 2) as price_per_liter,
                    fr.odometer_reading,
                    fr.station_name
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
            
            query += " ORDER BY fr.fuel_date DESC"
            
        elif report_type == 'maintenance_costs':
            query = """
                SELECT 
                    sm.service_date,
                    v.vehicle_number,
                    CONCAT(v.make, ' ', v.model) as vehicle,
                    sm.service_type,
                    sm.description,
                    sm.cost,
                    sm.status
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
                    va.assignment_date,
                    va.return_date,
                    v.vehicle_number,
                    CONCAT(v.make, ' ', v.model) as vehicle,
                    e.username as assigned_to,
                    va.purpose,
                    va.status,
                    va.mileage_at_assignment,
                    va.mileage_at_return,
                    (va.mileage_at_return - va.mileage_at_assignment) as distance
                FROM vehicle_assignments va
                JOIN vehicles v ON va.vehicle_id = v.id
                JOIN employees e ON va.employee_id = e.id
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
            return []
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def generate_excel_report(self, report, data, start_date, end_date):
        """Generate Excel report file"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Write to Excel
            df.to_excel(writer, sheet_name='Report', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Report']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.read()
    
    def generate_pdf_report(self, report, data, start_date, end_date):
        """Generate PDF report file"""
        output = io.BytesIO()
        
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>{report['report_name']}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Subtitle
        subtitle = Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles['Normal']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 12))
        
        # Table data
        if data:
            # Get column names
            columns = list(data[0].keys())
            table_data = [columns]
            
            # Add rows
            for row in data:
                table_data.append([str(row.get(col, '')) for col in columns])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        return output.read()
    
    def log_execution(self, cursor, report_id, status, records_count, error_message=None):
        """Log report execution"""
        cursor.execute("""
            INSERT INTO report_execution_log 
            (scheduled_report_id, execution_date, status, records_processed, error_message)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (report_id, status, records_count, error_message))
    
    def calculate_next_run(self, frequency):
        """Calculate next run date based on frequency"""
        now = datetime.now()
        
        if frequency == 'daily':
            next_run = now + timedelta(days=1)
        elif frequency == 'weekly':
            next_run = now + timedelta(weeks=1)
        elif frequency == 'monthly':
            # Next month, same day
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1)
            else:
                next_run = now.replace(month=now.month + 1)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.replace(hour=8, minute=0, second=0, microsecond=0)
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("✓ Background scheduler stopped")


# Global scheduler instance
scheduled_reports_manager = ScheduledReportsManager()
