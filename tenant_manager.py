"""
Multi-tenant database manager
Handles database isolation with separate database per tenant
"""

import pymysql
from contextlib import contextmanager
from flask import g, session
import threading

class TenantDatabaseManager:
    """
    Manages database connections for multi-tenant architecture
    Each tenant gets a separate MySQL database
    """
    
    # Main/Central database configuration (for companies table and tenant mapping)
    MAIN_DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'database': 'fleet_saas_main',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    # Base configuration for tenant databases
    TENANT_DB_BASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    # Thread-local storage for connections
    _local = threading.local()
    
    @classmethod
    def get_main_connection(cls):
        """Get connection to main database (companies/tenants info)"""
        return pymysql.connect(**cls.MAIN_DB_CONFIG)
    
    @classmethod
    def get_tenant_connection(cls, database_name):
        """Get connection to specific tenant database"""
        config = cls.TENANT_DB_BASE_CONFIG.copy()
        config['database'] = database_name
        return pymysql.connect(**config)
    
    @classmethod
    def create_tenant_database(cls, database_name):
        """
        Create a new database for a tenant
        Returns True if successful, False otherwise
        """
        try:
            connection = pymysql.connect(
                host=cls.TENANT_DB_BASE_CONFIG['host'],
                user=cls.TENANT_DB_BASE_CONFIG['user'],
                password=cls.TENANT_DB_BASE_CONFIG['password'],
                charset=cls.TENANT_DB_BASE_CONFIG['charset']
            )
            
            with connection.cursor() as cursor:
                # Create database
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
            
            connection.close()
            
            # Initialize tenant database with schema
            cls.initialize_tenant_schema(database_name)
            
            return True
        except Exception as e:
            print(f"Error creating tenant database: {e}")
            return False
    
    @classmethod
    def initialize_tenant_schema(cls, database_name):
        """
        Initialize tenant database with all required tables
        This creates the complete schema for a new tenant
        """
        import models
        import models_settings
        from models_tenant import TenantSettings
        import models_analytics
        
        connection = cls.get_tenant_connection(database_name)
        
        try:
            with connection.cursor() as cursor:
                # Create all tables from models.py SQL in correct order
                # (respecting foreign key dependencies)
                cursor.execute(models.CREATE_USERS_TABLE)
                cursor.execute(models.CREATE_EMPLOYEES_TABLE)
                cursor.execute(models.CREATE_VEHICLES_TABLE)
                cursor.execute(models.CREATE_VEHICLE_ASSIGNMENTS_TABLE)
                cursor.execute(models.CREATE_FUEL_RECORDS_TABLE)
                cursor.execute(models.CREATE_JOB_CARDS_TABLE)
                cursor.execute(models.CREATE_JOB_CARD_ITEMS_TABLE)
                cursor.execute(models.CREATE_SERVICE_MAINTENANCE_TABLE)
                cursor.execute(models.CREATE_SERVICE_REQUISITIONS_TABLE)
                
                # Create settings tables from models_settings.py
                cursor.execute(models_settings.CREATE_SYSTEM_SETTINGS_TABLE)
                cursor.execute(models_settings.CREATE_EMPLOYEE_PREFERENCES_TABLE)
                cursor.execute(models_settings.CREATE_NOTIFICATION_SETTINGS_TABLE)
                
                # Create analytics tables from models_analytics.py
                cursor.execute(models_analytics.CREATE_SCHEDULED_REPORTS_TABLE)
                cursor.execute(models_analytics.CREATE_REPORT_TEMPLATES_TABLE)
                cursor.execute(models_analytics.CREATE_KPI_SNAPSHOTS_TABLE)
                cursor.execute(models_analytics.CREATE_REPORT_LOG_TABLE)
                cursor.execute(models_analytics.CREATE_DASHBOARD_WIDGETS_TABLE)
                
                # Create tenant settings table
                TenantSettings.create_table(cursor)
                
                connection.commit()
            
            return True
        except Exception as e:
            print(f"Error initializing tenant schema: {e}")
            import traceback
            traceback.print_exc()
            connection.rollback()
            return False
        finally:
            connection.close()
    
    @classmethod
    def drop_tenant_database(cls, database_name):
        """
        Drop a tenant database (use with extreme caution!)
        Only for testing or when company is permanently deleted
        """
        try:
            connection = pymysql.connect(
                host=cls.TENANT_DB_BASE_CONFIG['host'],
                user=cls.TENANT_DB_BASE_CONFIG['user'],
                password=cls.TENANT_DB_BASE_CONFIG['password'],
                charset=cls.TENANT_DB_BASE_CONFIG['charset']
            )
            
            with connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{database_name}`")
                connection.commit()
            
            connection.close()
            return True
        except Exception as e:
            print(f"Error dropping tenant database: {e}")
            return False
    
    @classmethod
    def get_current_tenant_connection(cls):
        """
        Get connection for current tenant based on Flask context
        Uses g.tenant_db if available
        """
        if hasattr(g, 'tenant_db') and g.tenant_db:
            return cls.get_tenant_connection(g.tenant_db)
        else:
            raise Exception("No tenant context available. Use set_tenant_context() first.")
    
    @classmethod
    def set_tenant_context(cls, company_data):
        """
        Set tenant context for current request
        Stores tenant info in Flask's g object
        """
        g.tenant_id = company_data['id']
        g.tenant_db = company_data['database_name']
        g.tenant_name = company_data['name']
        g.tenant_subdomain = company_data['subdomain']
        g.tenant_plan = company_data['plan']
        g.tenant_status = company_data['status']
    
    @classmethod
    def clear_tenant_context(cls):
        """Clear tenant context"""
        if hasattr(g, 'tenant_id'):
            delattr(g, 'tenant_id')
        if hasattr(g, 'tenant_db'):
            delattr(g, 'tenant_db')
        if hasattr(g, 'tenant_name'):
            delattr(g, 'tenant_name')
        if hasattr(g, 'tenant_subdomain'):
            delattr(g, 'tenant_subdomain')
        if hasattr(g, 'tenant_plan'):
            delattr(g, 'tenant_plan')
        if hasattr(g, 'tenant_status'):
            delattr(g, 'tenant_status')
    
    @classmethod
    @contextmanager
    def main_db(cls):
        """Context manager for main database operations"""
        connection = cls.get_main_connection()
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()
    
    @classmethod
    @contextmanager
    def tenant_db(cls, database_name=None):
        """Context manager for tenant database operations"""
        if database_name is None:
            # Use current tenant from context
            if not hasattr(g, 'tenant_db'):
                raise Exception("No tenant context available")
            database_name = g.tenant_db
        
        connection = cls.get_tenant_connection(database_name)
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()


def init_main_database():
    """
    Initialize the main SaaS database with tenant management tables
    Run this once during initial setup
    """
    from models_tenant import Company, TenantUser
    
    try:
        # Create main database if it doesn't exist
        connection = pymysql.connect(
            host=TenantDatabaseManager.TENANT_DB_BASE_CONFIG['host'],
            user=TenantDatabaseManager.TENANT_DB_BASE_CONFIG['user'],
            password=TenantDatabaseManager.TENANT_DB_BASE_CONFIG['password'],
            charset=TenantDatabaseManager.TENANT_DB_BASE_CONFIG['charset']
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{TenantDatabaseManager.MAIN_DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
        
        connection.close()
        
        # Create tables in main database
        with TenantDatabaseManager.main_db() as conn:
            with conn.cursor() as cursor:
                Company.create_table(cursor)
                TenantUser.create_table(cursor)
                conn.commit()
        
        print("✅ Main SaaS database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing main database: {e}")
        return False


def get_db_connection():
    """
    Get database connection for current tenant
    This replaces the old get_db_connection() function
    """
    return TenantDatabaseManager.get_current_tenant_connection()
