"""
Multi-tenant middleware
Automatically identifies tenant from subdomain/domain and sets context
"""

from flask import request, g, redirect, url_for, session, abort
from functools import wraps
from tenant_manager import TenantDatabaseManager
from models_tenant import Company
import re

class TenantMiddleware:
    """
    Middleware to identify and set tenant context for each request
    Supports subdomain-based and custom domain-based tenant identification
    """
    
    # Main domain for the SaaS application
    MAIN_DOMAIN = 'fleetmanager.local'  # Change to your production domain
    
    # Routes that don't require tenant context
    PUBLIC_ROUTES = [
        'index',
        'tenant.tenant_signup',
        'tenant.check_subdomain',
        'tenant.tenant_select',
        'tenant.tenant_switch',
        'static',
        'health_check',
        'user_login',
        'user_signup',
        'employee_login',
        'employee_signup',
        'logout',
    ]
    
    # Super admin routes (no tenant context needed)
    ADMIN_ROUTES = [
        'super_admin_login',
        'super_admin_dashboard',
        'super_admin_companies',
    ]
    
    def __init__(self, app):
        self.app = app
        app.before_request(self.identify_tenant)
        app.teardown_request(self.cleanup_tenant)
    
    def identify_tenant(self):
        """
        Identify tenant from request and set context
        Called before each request
        """
        # Skip for static files
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # For login routes, try to use session tenant but don't enforce it
        login_routes = ['user_login', 'employee_login']
        is_login_route = request.endpoint in login_routes
        
        # Skip tenant identification for other public routes
        if not is_login_route and (request.endpoint in self.PUBLIC_ROUTES or request.endpoint in self.ADMIN_ROUTES):
            return
        
        try:
            # Get host from request
            host = request.host.lower()
            
            # Remove port if present
            if ':' in host:
                host = host.split(':')[0]
            
            # Try to identify tenant
            company = None
            
            # Method 1: Check if it's a subdomain
            if '.' in host:
                parts = host.split('.')
                
                # Check if it's a subdomain of main domain
                if len(parts) >= 3:  # e.g., acme.fleetmanager.local
                    subdomain = parts[0]
                    main_domain = '.'.join(parts[1:])
                    
                    if main_domain == self.MAIN_DOMAIN and subdomain != 'www':
                        # Look up company by subdomain
                        with TenantDatabaseManager.main_db() as conn:
                            with conn.cursor() as cursor:
                                company = Company.get_by_subdomain(cursor, subdomain)
                
                # Method 2: Check if it's a custom domain
                if not company:
                    with TenantDatabaseManager.main_db() as conn:
                        with conn.cursor() as cursor:
                            company = Company.get_by_domain(cursor, host)
            
            # Method 3: Use tenant from session (fallback for localhost development)
            if not company and 'tenant_id' in session:
                with TenantDatabaseManager.main_db() as conn:
                    with conn.cursor() as cursor:
                        company = Company.get_by_id(cursor, session['tenant_id'])
            
            # If tenant found, set context
            if company:
                # Check if tenant is active
                if company['status'] not in ['active', 'trial']:
                    return self.render_suspended_page(company)
                
                # Set tenant context
                TenantDatabaseManager.set_tenant_context(company)
                
                # Store in session for consistency
                session['tenant_id'] = company['id']
                session['tenant_name'] = company['name']
            else:
                # No tenant found
                # Allow login routes to proceed (they will show error if credentials invalid)
                if is_login_route:
                    return
                
                # For other routes, redirect to tenant selection or error
                if request.endpoint not in self.PUBLIC_ROUTES:
                    # For localhost development, allow access without strict tenant
                    if 'localhost' in host or '127.0.0.1' in host:
                        # Try to use default tenant or first available
                        with TenantDatabaseManager.main_db() as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("SELECT * FROM companies WHERE status IN ('active', 'trial') LIMIT 1")
                                company = cursor.fetchone()
                                if company:
                                    TenantDatabaseManager.set_tenant_context(company)
                                    session['tenant_id'] = company['id']
                                    session['tenant_name'] = company['name']
                                    return
                    
                    # Production: redirect to main site
                    return abort(404, "Company not found. Please check your URL.")
        
        except Exception as e:
            print(f"Error identifying tenant: {e}")
            # Don't break the application, continue without tenant context
            pass
    
    def cleanup_tenant(self, exception=None):
        """
        Cleanup tenant context after request
        Called after each request
        """
        TenantDatabaseManager.clear_tenant_context()
    
    def render_suspended_page(self, company):
        """Render page for suspended/expired accounts"""
        from flask import render_template_string
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Suspended - {{ company_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <style>
                body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }
                .card { border: none; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center p-5">
                                <i class="fas fa-exclamation-triangle text-warning" style="font-size: 4rem;"></i>
                                <h2 class="mt-4">Account {{ status|title }}</h2>
                                <p class="lead text-muted">{{ company_name }}'s account is currently {{ status }}.</p>
                                {% if status == 'suspended' %}
                                <p>Please contact support to reactivate your account.</p>
                                {% elif status == 'expired' %}
                                <p>Your subscription has expired. Please renew to continue using the service.</p>
                                {% endif %}
                                <div class="mt-4">
                                    <a href="mailto:support@fleetmanager.com" class="btn btn-primary btn-lg">
                                        <i class="fas fa-envelope me-2"></i>Contact Support
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template, 
                                     company_name=company['name'],
                                     status=company['status'])


def require_tenant(f):
    """
    Decorator to ensure tenant context is available
    Use on routes that require tenant data
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'tenant_id'):
            abort(404, "Tenant context not available")
        return f(*args, **kwargs)
    return decorated_function


def check_tenant_limits(limit_type):
    """
    Decorator to check tenant limits before allowing action
    limit_type: 'users', 'vehicles', etc.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'tenant_id'):
                abort(404, "Tenant context not available")
            
            from models_tenant import Company
            
            # Check limits
            with TenantDatabaseManager.main_db() as conn:
                with conn.cursor() as cursor:
                    limits = Company.check_limits(cursor, g.tenant_id)
                    
                    if not limits['valid']:
                        from flask import flash, redirect, url_for
                        flash(f"Subscription limit reached: {limits['message']}", 'danger')
                        return redirect(url_for('employee_dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_tenant_info():
    """
    Helper function to get current tenant info
    Returns dict with tenant details or None
    """
    if hasattr(g, 'tenant_id'):
        return {
            'id': g.tenant_id,
            'name': g.tenant_name,
            'subdomain': g.tenant_subdomain,
            'database': g.tenant_db,
            'plan': g.tenant_plan,
            'status': g.tenant_status
        }
    return None
