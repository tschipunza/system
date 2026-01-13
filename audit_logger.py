"""
Audit Trail Logger for Analytics Module
Tracks all user actions on reports and analytics
"""
from flask import request, session, g
from datetime import datetime
import json
import time

class AuditLogger:
    """Log analytics actions for compliance and security"""
    
    @staticmethod
    def log_action(action_type, resource_type=None, resource_id=None, details=None, execution_time_ms=None):
        """
        Log an analytics action to audit trail
        
        Args:
            action_type: Type of action (view_dashboard, export_excel, etc.)
            resource_type: Type of resource (dashboard, custom_report, scheduled_report)
            resource_id: ID of the resource accessed
            details: Additional context (dict) - filters, parameters, etc.
            execution_time_ms: Time taken to execute action in milliseconds
        """
        try:
            # Get database connection
            if hasattr(g, 'tenant_db'):
                from tenant_manager import TenantDatabaseManager
                connection = TenantDatabaseManager.get_tenant_connection(g.tenant_db)
            else:
                import pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='ts#h3ph3rd',
                    database='flask_auth_db',
                    cursorclass=pymysql.cursors.DictCursor
                )
            
            cursor = connection.cursor()
            
            # Get employee ID from session
            employee_id = session.get('employee_id')
            if not employee_id:
                return  # Don't log if not logged in
            
            # Get request metadata
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent', '') if request else None
            
            # Convert details to JSON
            details_json = json.dumps(details) if details else None
            
            # Insert audit log
            cursor.execute('''
                INSERT INTO analytics_audit_log 
                (employee_id, action_type, resource_type, resource_id, details, 
                 ip_address, user_agent, execution_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (employee_id, action_type, resource_type, resource_id, details_json,
                  ip_address, user_agent, execution_time_ms))
            
            connection.commit()
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Audit log error: {e}")
            # Don't fail the main request if audit logging fails
    
    @staticmethod
    def log_with_timing(action_type, resource_type=None, resource_id=None):
        """
        Decorator to automatically log action with execution time
        
        Usage:
            @audit_logger.log_with_timing('view_dashboard', 'dashboard')
            def dashboard():
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = int((time.time() - start_time) * 1000)  # Convert to ms
                
                AuditLogger.log_action(
                    action_type=action_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    execution_time_ms=execution_time
                )
                
                return result
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator
    
    @staticmethod
    def get_user_activity(employee_id, days=30, limit=100):
        """
        Get recent activity for a user
        
        Args:
            employee_id: Employee ID to fetch activity for
            days: Number of days to look back
            limit: Maximum number of records to return
        
        Returns:
            List of audit log entries
        """
        try:
            if hasattr(g, 'tenant_db'):
                from tenant_manager import TenantDatabaseManager
                connection = TenantDatabaseManager.get_tenant_connection(g.tenant_db)
            else:
                import pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='ts#h3ph3rd',
                    database='flask_auth_db',
                    cursorclass=pymysql.cursors.DictCursor
                )
            
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT * FROM analytics_audit_log
                WHERE employee_id = %s
                AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY created_at DESC
                LIMIT %s
            ''', (employee_id, days, limit))
            
            activity = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return activity
            
        except Exception as e:
            print(f"Error fetching user activity: {e}")
            return []
    
    @staticmethod
    def get_report_access_stats(resource_type, resource_id):
        """
        Get access statistics for a specific report
        
        Args:
            resource_type: Type of resource (custom_report, scheduled_report)
            resource_id: ID of the resource
        
        Returns:
            Dict with access statistics
        """
        try:
            if hasattr(g, 'tenant_db'):
                from tenant_manager import TenantDatabaseManager
                connection = TenantDatabaseManager.get_tenant_connection(g.tenant_db)
            else:
                import pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='ts#h3ph3rd',
                    database='flask_auth_db',
                    cursorclass=pymysql.cursors.DictCursor
                )
            
            cursor = connection.cursor()
            
            # Get access count
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_accesses,
                    COUNT(DISTINCT employee_id) as unique_users,
                    AVG(execution_time_ms) as avg_execution_time,
                    MAX(created_at) as last_accessed
                FROM analytics_audit_log
                WHERE resource_type = %s AND resource_id = %s
            ''', (resource_type, resource_id))
            
            stats = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return stats
            
        except Exception as e:
            print(f"Error fetching report stats: {e}")
            return None
    
    @staticmethod
    def get_analytics_summary(days=30):
        """
        Get summary of all analytics activity
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dict with activity summary
        """
        try:
            if hasattr(g, 'tenant_db'):
                from tenant_manager import TenantDatabaseManager
                connection = TenantDatabaseManager.get_tenant_connection(g.tenant_db)
            else:
                import pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='ts#h3ph3rd',
                    database='flask_auth_db',
                    cursorclass=pymysql.cursors.DictCursor
                )
            
            cursor = connection.cursor()
            
            # Get total actions and unique users
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_actions,
                    COUNT(DISTINCT employee_id) as unique_users,
                    AVG(execution_time_ms) as avg_execution_time
                FROM analytics_audit_log
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ''', (days,))
            
            overview = cursor.fetchone()
            
            # Get today's actions
            cursor.execute('''
                SELECT COUNT(*) as today_actions
                FROM analytics_audit_log
                WHERE DATE(created_at) = CURDATE()
            ''')
            
            today = cursor.fetchone()
            
            # Get activity by action type
            cursor.execute('''
                SELECT 
                    action_type,
                    COUNT(*) as count
                FROM analytics_audit_log
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY action_type
                ORDER BY count DESC
            ''', (days,))
            
            by_action_type = {row['action_type']: row['count'] for row in cursor.fetchall()}
            
            # Get most active users
            cursor.execute('''
                SELECT 
                    e.username,
                    e.email,
                    COUNT(*) as activity_count
                FROM analytics_audit_log a
                JOIN employees e ON a.employee_id = e.id
                WHERE a.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY a.employee_id, e.username, e.email
                ORDER BY activity_count DESC
                LIMIT 10
            ''', (days,))
            
            top_users = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                'total_actions': overview['total_actions'],
                'unique_users': overview['unique_users'],
                'avg_execution_time': overview['avg_execution_time'] or 0,
                'today_actions': today['today_actions'],
                'by_action_type': by_action_type,
                'top_users': top_users
            }
            
        except Exception as e:
            print(f"Error fetching analytics summary: {e}")
            return None

# Create global instance
audit_logger = AuditLogger()
