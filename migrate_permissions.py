"""
Migration script to create analytics_permissions table
for role-based access control
"""

import pymysql

# Database configurations
DATABASES = {
    'flask_auth_db': {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'database': 'flask_auth_db'
    },
    'fleet_twt': {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'database': 'fleet_twt'
    },
    'fleet_afroit': {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'database': 'fleet_afroit'
    }
}

# SQL to create permissions table
CREATE_PERMISSIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS analytics_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    permission VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_role_permission (role, permission),
    INDEX idx_role (role),
    INDEX idx_permission (permission)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
'''

# Default permissions for each role
DEFAULT_PERMISSIONS = [
    # Admin - Full access
    ('admin', 'view_dashboard', 'View analytics dashboard'),
    ('admin', 'view_all_reports', 'View all reports including other users data'),
    ('admin', 'export_excel', 'Export reports to Excel'),
    ('admin', 'export_pdf', 'Export reports to PDF'),
    ('admin', 'create_scheduled_reports', 'Create scheduled reports'),
    ('admin', 'delete_scheduled_reports', 'Delete scheduled reports'),
    ('admin', 'view_audit_trail', 'View audit trail logs'),
    ('admin', 'manage_permissions', 'Manage user permissions'),
    ('admin', 'view_kpis', 'View KPI dashboard'),
    
    # Manager - View and export, but limited to team data
    ('manager', 'view_dashboard', 'View analytics dashboard'),
    ('manager', 'view_team_reports', 'View reports for team members'),
    ('manager', 'export_excel', 'Export reports to Excel'),
    ('manager', 'export_pdf', 'Export reports to PDF'),
    ('manager', 'create_scheduled_reports', 'Create scheduled reports for team'),
    ('manager', 'view_kpis', 'View KPI dashboard'),
    
    # Employee - View only their own data
    ('employee', 'view_dashboard', 'View personal analytics dashboard'),
    ('employee', 'view_own_reports', 'View own reports only'),
    ('employee', 'export_excel', 'Export own reports to Excel'),
]

def migrate_database(db_name, db_config):
    """Migrate a single database"""
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # Create table
        cursor.execute(CREATE_PERMISSIONS_TABLE)
        
        # Insert default permissions
        insert_sql = '''
            INSERT IGNORE INTO analytics_permissions (role, permission, description)
            VALUES (%s, %s, %s)
        '''
        cursor.executemany(insert_sql, DEFAULT_PERMISSIONS)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✓ analytics_permissions table created and populated in {db_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {db_name}: {e}")
        return False

def main():
    print("=" * 70)
    print("Analytics Role-Based Permissions Migration")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for db_name, db_config in DATABASES.items():
        if migrate_database(db_name, db_config):
            success_count += 1
        else:
            fail_count += 1
    
    print("=" * 70)
    print(f"Migration Summary:")
    print(f"  Total databases: {len(DATABASES)}")
    print(f"  Successfully migrated: {success_count}")
    print(f"  Failed: {fail_count}")
    print("=" * 70)
    
    if success_count == len(DATABASES):
        print("\n✓ Role-based permissions enabled!")
        print("\nPermission Levels:")
        print("  • Admin: Full access to all analytics features")
        print("  • Manager: View team reports, export, create scheduled reports")
        print("  • Employee: View and export own data only")

if __name__ == '__main__':
    main()
