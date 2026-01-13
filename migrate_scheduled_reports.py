"""
Migrate Scheduled Reports Tables to All Databases
"""
import pymysql
from config import Config

# Updated scheduled reports table with correct structure
CREATE_SCHEDULED_REPORTS_TABLE = '''
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    report_type ENUM('fuel_analysis', 'maintenance_costs', 'vehicle_assignments') NOT NULL,
    frequency ENUM('daily', 'weekly', 'monthly') NOT NULL,
    format ENUM('excel', 'pdf') DEFAULT 'excel',
    recipients TEXT NOT NULL COMMENT 'Comma-separated email addresses',
    filters JSON COMMENT 'Report filter parameters',
    is_active BOOLEAN DEFAULT TRUE,
    next_run_date DATETIME,
    last_run_date DATETIME,
    execution_count INT DEFAULT 0,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_next_run (next_run_date),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
'''

# Report execution log table
CREATE_REPORT_LOG_TABLE = '''
CREATE TABLE IF NOT EXISTS report_execution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheduled_report_id INT,
    executed_at DATETIME NOT NULL,
    status ENUM('success', 'failed') NOT NULL,
    records_count INT DEFAULT 0,
    recipients_count INT DEFAULT 0,
    execution_time_seconds DECIMAL(8,2),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_id (scheduled_report_id),
    INDEX idx_executed_at (executed_at),
    FOREIGN KEY (scheduled_report_id) REFERENCES scheduled_reports(id) ON DELETE CASCADE
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
        
        # Create scheduled_reports table
        print(f"  Creating scheduled_reports table...")
        cursor.execute(CREATE_SCHEDULED_REPORTS_TABLE)
        print(f"  ✓ scheduled_reports table created")
        
        # Create report_execution_log table
        print(f"  Creating report_execution_log table...")
        cursor.execute(CREATE_REPORT_LOG_TABLE)
        print(f"  ✓ report_execution_log table created")
        
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
    print("Scheduled Reports Tables Migration")
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
        print("\nNext steps:")
        print("1. Restart the Flask application")
        print("2. Navigate to Analytics > Scheduled Reports")
        print("3. Create your first scheduled report")
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
