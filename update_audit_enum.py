"""
Add unauthorized_access action type to analytics_audit_log
"""

import pymysql

DATABASES = ['flask_auth_db', 'fleet_twt', 'fleet_afroit']

def update_database(db_name):
    """Update a single database"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database=db_name
        )
        
        cursor = connection.cursor()
        
        # Alter the enum to add unauthorized_access
        cursor.execute("""
            ALTER TABLE analytics_audit_log 
            MODIFY COLUMN action_type ENUM(
                'view_dashboard',
                'view_report', 
                'export_excel',
                'export_pdf',
                'create_scheduled_report',
                'delete_scheduled_report',
                'run_scheduled_report',
                'unauthorized_access'
            ) NOT NULL
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✓ Updated {db_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error updating {db_name}: {e}")
        return False

def main():
    print("=" * 70)
    print("Adding unauthorized_access action type to audit log")
    print("=" * 70)
    
    for db_name in DATABASES:
        update_database(db_name)
    
    print("=" * 70)
    print("✓ Update complete!")

if __name__ == '__main__':
    main()
