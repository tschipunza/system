"""
Permission Manager for Role-Based Access Control
Handles checking and managing user permissions for analytics features
"""

from flask import session, g, flash, redirect, url_for, request
from functools import wraps
import pymysql

class PermissionManager:
    """Manages role-based permissions for analytics features"""
    
    # Permission cache to avoid repeated database queries
    _permission_cache = {}
    
    @staticmethod
    def get_user_role():
        """
        Get the current user's role from session
        
        Returns:
            str: Role name (admin, manager, employee) or None
        """
        return session.get('role', 'employee')  # Default to employee if not set
    
    @staticmethod
    def get_user_permissions(role=None):
        """
        Get all permissions for a role
        
        Args:
            role: Role to get permissions for (uses current user's role if not specified)
        
        Returns:
            set: Set of permission strings
        """
        if role is None:
            role = PermissionManager.get_user_role()
        
        # Check cache first
        if role in PermissionManager._permission_cache:
            return PermissionManager._permission_cache[role]
        
        try:
            # Get database connection
            if hasattr(g, 'tenant_db'):
                from tenant_manager import TenantDatabaseManager
                connection = TenantDatabaseManager.get_tenant_connection(g.tenant_db)
            else:
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='ts#h3ph3rd',
                    database='flask_auth_db',
                    cursorclass=pymysql.cursors.DictCursor
                )
            
            cursor = connection.cursor()
            
            # Try new role system first (roles + permissions + role_permissions tables)
            try:
                cursor.execute('''
                    SELECT p.permission_key
                    FROM permissions p
                    INNER JOIN role_permissions rp ON p.id = rp.permission_id
                    INNER JOIN roles r ON r.id = rp.role_id
                    WHERE r.role_key = %s
                ''', (role,))
                
                permissions = {row['permission_key'] for row in cursor.fetchall()}
                
                # Also add analytics permissions for backward compatibility
                cursor.execute('''
                    SELECT permission FROM analytics_permissions
                    WHERE role = %s
                ''', (role,))
                
                analytics_perms = {row['permission'] for row in cursor.fetchall()}
                permissions.update(analytics_perms)
                
            except Exception as inner_e:
                # Fallback to old analytics_permissions table
                print(f"Using analytics_permissions fallback: {inner_e}")
                cursor.execute('''
                    SELECT permission FROM analytics_permissions
                    WHERE role = %s
                ''', (role,))
                
                permissions = {row['permission'] for row in cursor.fetchall()}
            
            cursor.close()
            connection.close()
            
            # Cache the results
            PermissionManager._permission_cache[role] = permissions
            
            return permissions
            
        except Exception as e:
            print(f"Error fetching permissions: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal permissions on error
            return {'view_dashboard'} if role == 'employee' else set()
    
    @staticmethod
    def has_permission(permission):
        """
        Check if current user has a specific permission
        
        Args:
            permission: Permission string to check
        
        Returns:
            bool: True if user has permission, False otherwise
        """
        user_permissions = PermissionManager.get_user_permissions()
        return permission in user_permissions
    
    @staticmethod
    def clear_cache():
        """Clear the permission cache (call when permissions are updated)"""
        PermissionManager._permission_cache.clear()
    
    @staticmethod
    def can_view_user_data(target_employee_id):
        """
        Check if current user can view data for a specific employee
        
        Args:
            target_employee_id: ID of the employee whose data is being accessed
        
        Returns:
            bool: True if access is allowed, False otherwise
        """
        role = PermissionManager.get_user_role()
        current_user_id = session.get('employee_id')
        
        # Admin can view all data
        if PermissionManager.has_permission('view_all_reports'):
            return True
        
        # Manager can view team data (implement team logic as needed)
        if PermissionManager.has_permission('view_team_reports'):
            # TODO: Implement team membership check
            # For now, managers can view all data
            return True
        
        # Employee can only view own data
        if PermissionManager.has_permission('view_own_reports'):
            return int(target_employee_id) == int(current_user_id)
        
        return False
    
    @staticmethod
    def filter_query_by_role(base_query, employee_field='employee_id'):
        """
        Modify a SQL query to filter data based on user role
        
        Args:
            base_query: Base SQL query to filter
            employee_field: Name of the employee ID field in the query
        
        Returns:
            tuple: (filtered_query, params) Modified query and parameters
        """
        role = PermissionManager.get_user_role()
        current_user_id = session.get('employee_id')
        
        # Admin sees all data - no filter needed
        if PermissionManager.has_permission('view_all_reports'):
            return base_query, []
        
        # Manager sees team data - for now, all data (TODO: implement team filtering)
        if PermissionManager.has_permission('view_team_reports'):
            return base_query, []
        
        # Employee sees only own data
        if PermissionManager.has_permission('view_own_reports'):
            # Add WHERE clause or AND condition
            if 'WHERE' in base_query.upper():
                filtered_query = base_query + f' AND {employee_field} = %s'
            else:
                filtered_query = base_query + f' WHERE {employee_field} = %s'
            return filtered_query, [current_user_id]
        
        # No permissions - return query that returns nothing
        return base_query + ' WHERE 1=0', []


def require_permission(permission):
    """
    Decorator to protect routes with permission checks
    
    Args:
        permission: Permission string required to access the route
    
    Usage:
        @require_permission('export_excel')
        def export_report():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'employee_id' not in session:
                flash('Please log in to access this feature.', 'warning')
                return redirect(url_for('employee_login'))
            
            # Check if user has required permission
            if not PermissionManager.has_permission(permission):
                flash(f'You do not have permission to access this feature. Required: {permission}', 'danger')
                
                # Log unauthorized access attempt
                try:
                    from audit_logger import audit_logger
                    audit_logger.log_action(
                        'unauthorized_access',
                        'analytics',
                        details={'required_permission': permission, 'url': request.url}
                    )
                except:
                    pass
                
                return redirect(url_for('analytics.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_permission_context():
    """
    Get permission context for templates
    
    Returns:
        dict: Dictionary of permissions for current user
    """
    permissions = PermissionManager.get_user_permissions()
    
    context = {
        'can_view_dashboard': 'view_dashboard' in permissions,
        'can_view_all_reports': 'view_all_reports' in permissions,
        'can_view_team_reports': 'view_team_reports' in permissions,
        'can_view_own_reports': 'view_own_reports' in permissions,
        'can_export_excel': 'export_excel' in permissions,
        'can_export_pdf': 'export_pdf' in permissions,
        'can_create_scheduled_reports': 'create_scheduled_reports' in permissions,
        'can_delete_scheduled_reports': 'delete_scheduled_reports' in permissions,
        'can_view_audit_trail': 'view_audit_trail' in permissions,
        'can_manage_permissions': 'manage_permissions' in permissions,
        'can_view_kpis': 'view_kpis' in permissions,
        'user_role': PermissionManager.get_user_role()
    }
    
    # Debug: Print permissions
    print(f"Permission Context - Role: {context['user_role']}, Total permissions: {len(permissions)}")
    print(f"  Scheduled Reports: {context['can_create_scheduled_reports']}, Audit Trail: {context['can_view_audit_trail']}")
    
    return context


# Create global instance
permission_manager = PermissionManager()
