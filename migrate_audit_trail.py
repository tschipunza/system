"""
Create Audit Trail Table for Analytics Reports
Tracks all report views, exports, and data access
"""
import pymysql

CREATE_AUDIT_TABLE = '''
CREATE TABLE IF NOT EXISTS analytics_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    action_type ENUM('view_dashboard', 'view_report', 'export_excel', 'export_pdf', 
                     'run_scheduled_report', 'create_scheduled_report', 'delete_scheduled_report') NOT NULL,
    resource_type VARCHAR(50) COMMENT 'dashboard, custom_report, scheduled_report',
    resource_id INT COMMENT 'ID of report or resource accessed',
    details JSON COMMENT 'Additional context like filters, date ranges, report name',
    ip_address VARCHAR(45),
    user_agent TEXT,
    execution_time_ms INT COMMENT 'Time taken to generate report',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at),
    INDEX idx_resource (resource_type, resource_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
'''

def migrate_database(database_name):
    """Migrate a single database"""
    print(f"\nMigrating database: {database_name}")
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database=database_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        # Create audit log table
        print(f"  Creating analytics_audit_log table...")
        cursor.execute(CREATE_AUDIT_TABLE)
        print(f"  ✓ analytics_audit_log table created")
        
        connection.commit()
        print(f"✓ Successfully migrated {database_name}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {database_name}: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 70)
    print("Analytics Audit Trail Migration")
    print("=" * 70)
    
    # List of databases to migrate
    databases = [
        'flask_auth_db',  # Main database
        'fleet_twt',      # Tenant 1
        'fleet_afroit'    # Tenant 2
    ]
    
    success_count = 0
    failed_count = 0
    
    for db in databases:
        if migrate_database(db):
            success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 70)
    print("Migration Summary")
    print("=" * 70)
    print(f"Total databases: {len(databases)}")
    print(f"✓ Successfully migrated: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print("=" * 70)
    
    if failed_count == 0:
        print("\n✓ All databases migrated successfully!")
        print("\nAudit trail is now enabled for:")
        print("  - Dashboard views")
        print("  - Report generations")
        print("  - Excel/PDF exports")
        print("  - Scheduled report actions")
    else:
        print("\n⚠ Some databases failed to migrate. Check the errors above.")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
