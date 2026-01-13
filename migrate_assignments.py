"""
Quick migration script to migrate vehicle_assignments table only
"""

import pymysql
from tenant_manager import TenantDatabaseManager

def migrate_assignments():
    print("Migrating vehicle_assignments from flask_auth_db to fleet_twt...")
    
    try:
        # Connect to old database
        old_conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database='flask_auth_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        old_cursor = old_conn.cursor()
        
        # Connect to new tenant database
        new_conn = TenantDatabaseManager.get_tenant_connection('fleet_twt')
        new_cursor = new_conn.cursor()
        
        # Get all vehicle assignments
        old_cursor.execute("SELECT * FROM vehicle_assignments")
        assignments = old_cursor.fetchall()
        
        print(f"Found {len(assignments)} vehicle assignments to migrate")
        
        if assignments:
            # Get column names
            old_cursor.execute("DESCRIBE vehicle_assignments")
            columns = [col['Field'] for col in old_cursor.fetchall()]
            
            # Verify columns in new database
            new_cursor.execute("DESCRIBE vehicle_assignments")
            new_columns = [col['Field'] for col in new_cursor.fetchall()]
            
            # Use only common columns
            common_columns = [col for col in columns if col in new_columns]
            print(f"Migrating columns: {', '.join(common_columns)}")
            
            # Insert each assignment
            count = 0
            for assignment in assignments:
                try:
                    values = [assignment[col] for col in common_columns]
                    placeholders = ', '.join(['%s'] * len(common_columns))
                    column_names = ', '.join(common_columns)
                    
                    insert_query = f"INSERT INTO vehicle_assignments ({column_names}) VALUES ({placeholders})"
                    new_cursor.execute(insert_query, values)
                    count += 1
                except pymysql.err.IntegrityError as e:
                    if 'Duplicate entry' in str(e):
                        print(f"  Skipping duplicate: ID {assignment['id']}")
                        continue
                    else:
                        print(f"  Error: {e}")
                        continue
            
            new_conn.commit()
            print(f"✓ Successfully migrated {count} vehicle assignments")
        else:
            print("No assignments to migrate")
        
        # Close connections
        old_cursor.close()
        old_conn.close()
        new_cursor.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    migrate_assignments()
