"""
Permissions Helper Module
Provides functions to check user permissions and control access
"""
from functools import wraps
from flask import session, flash, redirect, url_for
from app import get_db_connection

def get_user_permissions(user_id):
    """Get all permissions for a user based on their role"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user's role
        cursor.execute("SELECT role FROM employees WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['role']:
            return []
        
        role_key = user['role']
        
        # Get role ID
        cursor.execute("SELECT id FROM roles WHERE role_key = %s", (role_key,))
        role = cursor.fetchone()
        
        if not role:
            return []
        
        # Get all permissions for this role
        cursor.execute("""
            SELECT p.permission_key, p.permission_name, p.description, p.module
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = %s
        """, (role['id'],))
        
        permissions = cursor.fetchall()
        return [p['permission_key'] for p in permissions]
        
    finally:
        cursor.close()
        conn.close()


def has_permission(user_id, permission_key):
    """Check if user has a specific permission"""
    permissions = get_user_permissions(user_id)
    return permission_key in permissions


def has_any_permission(user_id, permission_keys):
    """Check if user has any of the specified permissions"""
    permissions = get_user_permissions(user_id)
    return any(perm in permissions for perm in permission_keys)


def has_all_permissions(user_id, permission_keys):
    """Check if user has all of the specified permissions"""
    permissions = get_user_permissions(user_id)
    return all(perm in permissions for perm in permission_keys)


def permission_required(permission_key, redirect_to='employee_dashboard'):
    """
    Decorator to protect routes with permission check
    Usage: @permission_required('add_vehicle')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'employee_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('index'))
            
            if not has_permission(session['employee_id'], permission_key):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for(redirect_to))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def any_permission_required(permission_keys, redirect_to='employee_dashboard'):
    """
    Decorator to protect routes - requires any of the specified permissions
    Usage: @any_permission_required(['add_vehicle', 'edit_vehicle'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'employee_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('index'))
            
            if not has_any_permission(session['employee_id'], permission_keys):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for(redirect_to))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_role_permissions(role_key):
    """Get all permissions for a specific role"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.permission_key, p.permission_name, p.description, p.module
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN roles r ON rp.role_id = r.id
            WHERE r.role_key = %s
            ORDER BY p.module, p.permission_name
        """, (role_key,))
        
        return cursor.fetchall()
        
    finally:
        cursor.close()
        conn.close()


def get_all_permissions():
    """Get all available permissions grouped by module"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, permission_key, permission_name, description, module
            FROM permissions
            ORDER BY module, permission_name
        """)
        
        permissions = cursor.fetchall()
        
        # Group by module
        grouped = {}
        for perm in permissions:
            module = perm['module'] or 'Other'
            if module not in grouped:
                grouped[module] = []
            grouped[module].append(perm)
        
        return grouped
        
    finally:
        cursor.close()
        conn.close()


def get_all_roles():
    """Get all roles with their permission counts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.id, r.role_key, r.role_name, r.description, r.is_system_role,
                   COUNT(rp.permission_id) as permission_count
            FROM roles r
            LEFT JOIN role_permissions rp ON r.id = rp.role_id
            GROUP BY r.id
            ORDER BY r.role_name
        """)
        
        return cursor.fetchall()
        
    finally:
        cursor.close()
        conn.close()


def update_role_permissions(role_id, permission_ids):
    """Update permissions for a role"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete existing permissions
        cursor.execute("DELETE FROM role_permissions WHERE role_id = %s", (role_id,))
        
        # Insert new permissions
        for perm_id in permission_ids:
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (%s, %s)
            """, (role_id, perm_id))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating role permissions: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def create_custom_role(role_key, role_name, description, permission_ids):
    """Create a new custom role with specified permissions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert role
        cursor.execute("""
            INSERT INTO roles (role_key, role_name, description, is_system_role)
            VALUES (%s, %s, %s, FALSE)
        """, (role_key, role_name, description))
        
        role_id = cursor.lastrowid
        
        # Insert permissions
        for perm_id in permission_ids:
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (%s, %s)
            """, (role_id, perm_id))
        
        conn.commit()
        return role_id
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating role: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
