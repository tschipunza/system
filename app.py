from flask import Flask, g
import pymysql
from config import Config
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

# Template filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to Python object"""
    if value:
        try:
            return json.loads(value)
        except:
            return {}
    return {}

# Upload folder configuration
UPLOAD_FOLDER_FUEL = 'static/uploads/fuel_receipts'
UPLOAD_FOLDER_SERVICE = 'static/uploads/service_invoices'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_FUEL
app.config['UPLOAD_FOLDER_SERVICE'] = UPLOAD_FOLDER_SERVICE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folders if they don't exist
os.makedirs(UPLOAD_FOLDER_FUEL, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SERVICE, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Multi-tenant support
MULTI_TENANT_ENABLED = os.environ.get('MULTI_TENANT_ENABLED', 'true').lower() == 'true'

if MULTI_TENANT_ENABLED:
    # Use multi-tenant database manager
    from tenant_manager import TenantDatabaseManager
    from tenant_middleware import TenantMiddleware
    
    # Initialize tenant middleware
    TenantMiddleware(app)
    
    # Database connection function for multi-tenant
    def get_db_connection():
        """Get database connection for current tenant"""
        if hasattr(g, 'tenant_db'):
            return TenantDatabaseManager.get_tenant_connection(g.tenant_db)
        else:
            # Fallback for non-tenant routes or development
            return pymysql.connect(
                host='localhost',
                user='root',
                password='ts#h3ph3rd',
                database='flask_auth_db',
                cursorclass=pymysql.cursors.DictCursor
            )
else:
    # Legacy single-tenant mode
    def get_db_connection():
        return pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database='flask_auth_db',
            cursorclass=pymysql.cursors.DictCursor
        )

# Import routes after app initialization
from routes import *

# Register tenant routes if multi-tenant is enabled
if MULTI_TENANT_ENABLED:
    try:
        from routes_tenant import tenant_bp
        if 'tenant' not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(tenant_bp)
    except Exception as e:
        print(f"Note: Tenant routes registration: {e}")

# Register analytics blueprint
try:
    from routes_analytics import analytics_bp
    if 'analytics' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(analytics_bp)
        print("✓ Analytics module registered")
except Exception as e:
    print(f"Note: Analytics routes registration: {e}")

# Add global context processor for permissions
@app.context_processor
def inject_global_permissions():
    """Inject permission context into all templates globally"""
    try:
        # Only get permissions if user is logged in
        if 'employee_id' in session or 'user_id' in session:
            from permission_manager import get_permission_context
            return get_permission_context()
        else:
            # Not logged in, return empty permissions
            return {
                'can_view_dashboard': False,
                'can_view_all_reports': False,
                'can_view_team_reports': False,
                'can_view_own_reports': False,
                'can_export_excel': False,
                'can_export_pdf': False,
                'can_create_scheduled_reports': False,
                'can_delete_scheduled_reports': False,
                'can_view_audit_trail': False,
                'can_manage_permissions': False,
                'can_view_kpis': False,
                'user_role': None
            }
    except Exception as e:
        print(f"Error in inject_global_permissions: {e}")
        import traceback
        traceback.print_exc()
        # Return empty permissions if error
        return {
            'can_view_dashboard': False,
            'can_view_all_reports': False,
            'can_view_team_reports': False,
            'can_view_own_reports': False,
            'can_export_excel': False,
            'can_export_pdf': False,
            'can_create_scheduled_reports': False,
            'can_delete_scheduled_reports': False,
            'can_view_audit_trail': False,
            'can_manage_permissions': False,
            'can_view_kpis': False,
            'user_role': None
        }

# Initialize scheduled reports manager
try:
    from scheduler import scheduled_reports_manager
    scheduled_reports_manager.init_app(app)
    # Load scheduled reports after a short delay
    import threading
    def load_reports():
        import time
        time.sleep(2)  # Wait for app to fully start
        with app.app_context():
            scheduled_reports_manager.load_scheduled_reports()
    threading.Thread(target=load_reports, daemon=True).start()
    print("✓ Scheduled reports manager initialized")
except Exception as e:
    print(f"Note: Scheduler initialization: {e}")

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Cleanup scheduler on exit
        try:
            from scheduler import scheduled_reports_manager
            scheduled_reports_manager.stop()
        except:
            pass