"""
Multi-tenant models for SaaS architecture
Handles company/tenant management with database isolation
"""

from datetime import datetime

class Company:
    """
    Company/Tenant model
    Each company gets isolated database access
    """
    
    TABLE_NAME = 'companies'
    
    # Subscription Plans
    PLAN_TRIAL = 'trial'
    PLAN_BASIC = 'basic'
    PLAN_PROFESSIONAL = 'professional'
    PLAN_ENTERPRISE = 'enterprise'
    
    # Status
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_TRIAL = 'trial'
    STATUS_EXPIRED = 'expired'
    
    @staticmethod
    def create_table(cursor):
        """Create companies table in main database"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                subdomain VARCHAR(100) UNIQUE NOT NULL,
                custom_domain VARCHAR(255) UNIQUE NULL,
                database_name VARCHAR(100) UNIQUE NOT NULL,
                
                -- Contact Information
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                address TEXT,
                
                -- Subscription
                plan VARCHAR(50) NOT NULL DEFAULT 'trial',
                status VARCHAR(50) NOT NULL DEFAULT 'trial',
                max_users INT DEFAULT 5,
                max_vehicles INT DEFAULT 10,
                trial_ends_at DATETIME,
                subscription_ends_at DATETIME,
                
                -- Branding
                company_logo VARCHAR(500),
                primary_color VARCHAR(20) DEFAULT '#556ee6',
                
                -- Settings
                settings JSON,
                
                -- Timestamps
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_subdomain (subdomain),
                INDEX idx_custom_domain (custom_domain),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
    @staticmethod
    def create(cursor, name, subdomain, email, phone=None, plan='trial'):
        """Create a new company/tenant"""
        # Generate database name from subdomain
        database_name = f"fleet_{subdomain.lower().replace('-', '_')}"
        
        # Set trial end date (30 days from now)
        from datetime import timedelta
        trial_ends_at = datetime.now() + timedelta(days=30)
        
        cursor.execute('''
            INSERT INTO companies 
            (name, subdomain, database_name, email, phone, plan, status, trial_ends_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, subdomain, database_name, email, phone, plan, Company.STATUS_TRIAL, trial_ends_at))
        
        return cursor.lastrowid
    
    @staticmethod
    def get_by_subdomain(cursor, subdomain):
        """Get company by subdomain"""
        cursor.execute('''
            SELECT * FROM companies 
            WHERE subdomain = %s AND status IN ('active', 'trial')
        ''', (subdomain,))
        return cursor.fetchone()
    
    @staticmethod
    def get_by_domain(cursor, domain):
        """Get company by custom domain"""
        cursor.execute('''
            SELECT * FROM companies 
            WHERE custom_domain = %s AND status IN ('active', 'trial')
        ''', (domain,))
        return cursor.fetchone()
    
    @staticmethod
    def get_by_id(cursor, company_id):
        """Get company by ID"""
        cursor.execute('SELECT * FROM companies WHERE id = %s', (company_id,))
        return cursor.fetchone()
    
    @staticmethod
    def get_all(cursor, status=None):
        """Get all companies, optionally filtered by status"""
        if status:
            cursor.execute('SELECT * FROM companies WHERE status = %s ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM companies ORDER BY created_at DESC')
        return cursor.fetchall()
    
    @staticmethod
    def update_status(cursor, company_id, status):
        """Update company status"""
        cursor.execute('''
            UPDATE companies 
            SET status = %s 
            WHERE id = %s
        ''', (status, company_id))
    
    @staticmethod
    def update_subscription(cursor, company_id, plan, subscription_ends_at):
        """Update subscription plan and expiry"""
        cursor.execute('''
            UPDATE companies 
            SET plan = %s, subscription_ends_at = %s, status = %s
            WHERE id = %s
        ''', (plan, subscription_ends_at, Company.STATUS_ACTIVE, company_id))
    
    @staticmethod
    def check_limits(cursor, company_id):
        """Check if company is within its plan limits"""
        cursor.execute('''
            SELECT plan, max_users, max_vehicles, status, trial_ends_at, subscription_ends_at
            FROM companies WHERE id = %s
        ''', (company_id,))
        company = cursor.fetchone()
        
        if not company:
            return {'valid': False, 'message': 'Company not found'}
        
        # Check status
        if company[3] not in [Company.STATUS_ACTIVE, Company.STATUS_TRIAL]:
            return {'valid': False, 'message': 'Subscription inactive or suspended'}
        
        # Check trial expiry
        if company[3] == Company.STATUS_TRIAL and company[4] and company[4] < datetime.now():
            return {'valid': False, 'message': 'Trial period expired'}
        
        # Check subscription expiry
        if company[3] == Company.STATUS_ACTIVE and company[5] and company[5] < datetime.now():
            return {'valid': False, 'message': 'Subscription expired'}
        
        return {'valid': True, 'plan': company[0], 'max_users': company[1], 'max_vehicles': company[2]}


class TenantSettings:
    """
    Settings specific to each tenant
    Stored in tenant's database
    """
    
    TABLE_NAME = 'tenant_settings'
    
    @staticmethod
    def create_table(cursor):
        """Create tenant settings table in tenant database"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenant_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type VARCHAR(50) DEFAULT 'string',
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_key (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Insert default settings
        default_settings = [
            ('company_name', '', 'string', 'Company display name'),
            ('company_email', '', 'email', 'Company contact email'),
            ('company_phone', '', 'phone', 'Company phone number'),
            ('company_address', '', 'text', 'Company address'),
            ('default_fuel_consumption_threshold', '18', 'number', 'Default fuel consumption in km/L'),
            ('currency', 'USD', 'string', 'Default currency'),
            ('date_format', 'Y-m-d', 'string', 'Date format'),
            ('timezone', 'UTC', 'string', 'Default timezone'),
            ('whatsapp_enabled', '0', 'boolean', 'Enable WhatsApp notifications'),
            ('email_notifications', '1', 'boolean', 'Enable email notifications'),
        ]
        
        for key, value, type_, desc in default_settings:
            try:
                cursor.execute('''
                    INSERT INTO tenant_settings (setting_key, setting_value, setting_type, description)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = setting_value
                ''', (key, value, type_, desc))
            except:
                pass


class TenantUser:
    """
    Map users to their tenants
    Users can belong to multiple companies (different roles)
    """
    
    TABLE_NAME = 'tenant_users'
    
    @staticmethod
    def create_table(cursor):
        """Create tenant_users mapping table in main database"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenant_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                user_id INT NOT NULL,
                user_type ENUM('user', 'employee') NOT NULL,
                role VARCHAR(100) DEFAULT 'user',
                is_owner BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE KEY unique_tenant_user (company_id, user_id, user_type),
                INDEX idx_company (company_id),
                INDEX idx_user (user_id, user_type),
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
    
    @staticmethod
    def add_user_to_tenant(cursor, company_id, user_id, user_type, role='user', is_owner=False):
        """Add user to a tenant"""
        cursor.execute('''
            INSERT INTO tenant_users (company_id, user_id, user_type, role, is_owner)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE is_active = TRUE
        ''', (company_id, user_id, user_type, role, is_owner))
    
    @staticmethod
    def get_user_tenants(cursor, user_id, user_type):
        """Get all tenants for a user"""
        cursor.execute('''
            SELECT c.*, tu.role, tu.is_owner
            FROM tenant_users tu
            JOIN companies c ON tu.company_id = c.id
            WHERE tu.user_id = %s AND tu.user_type = %s AND tu.is_active = TRUE
            AND c.status IN ('active', 'trial')
            ORDER BY tu.created_at DESC
        ''', (user_id, user_type))
        return cursor.fetchall()
    
    @staticmethod
    def verify_user_access(cursor, company_id, user_id, user_type):
        """Verify if user has access to tenant"""
        cursor.execute('''
            SELECT * FROM tenant_users
            WHERE company_id = %s AND user_id = %s AND user_type = %s AND is_active = TRUE
        ''', (company_id, user_id, user_type))
        return cursor.fetchone() is not None
    
    @staticmethod
    def remove_user_from_tenant(cursor, company_id, user_id, user_type):
        """Remove user from tenant"""
        cursor.execute('''
            UPDATE tenant_users 
            SET is_active = FALSE
            WHERE company_id = %s AND user_id = %s AND user_type = %s
        ''', (company_id, user_id, user_type))
