"""
Migration script to ensure employees table has role column in all databases
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

def migrate_database(db_name, db_config):
    """Ensure role column exists in employees table"""
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        print(f"\n🔧 Checking {db_name}...")
        
        # Check if employees table exists
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'employees'
        """, (db_config['database'],))
        
        if cursor.fetchone()['count'] == 0:
            print(f"  ℹ No employees table found in {db_name}")
            cursor.close()
            connection.close()
            return True
        
        # Check if role column exists
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = 'employees' 
            AND column_name = 'role'
        """, (db_config['database'],))
        
        if cursor.fetchone()['count'] > 0:
            print(f"  ✓ Role column already exists")
            
            # Update any NULL or empty roles to 'employee'
            cursor.execute("""
                UPDATE employees 
                SET role = 'employee' 
                WHERE role IS NULL OR role = '' OR role = 'NULL'
            """)
            updated = cursor.rowcount
            connection.commit()
            
            if updated > 0:
                print(f"  ✓ Updated {updated} employees with default role")
            
            # Show current role distribution
            cursor.execute("""
                SELECT role, COUNT(*) as count 
                FROM employees 
                GROUP BY role
            """)
            roles = cursor.fetchall()
            print(f"  Role distribution:")
            for r in roles:
                print(f"    - {r['role']}: {r['count']} employees")
            
        else:
            # Add role column
            print(f"  Adding role column...")
            cursor.execute("""
                ALTER TABLE employees 
                ADD COLUMN role VARCHAR(50) DEFAULT 'employee' AFTER password_hash
            """)
            
            # Set default role for existing employees
            cursor.execute("""
                UPDATE employees 
                SET role = 'employee' 
                WHERE role IS NULL OR role = ''
            """)
            
            connection.commit()
            print(f"  ✓ Role column added successfully")
            
            # Show employee count
            cursor.execute("SELECT COUNT(*) as count FROM employees")
            emp_count = cursor.fetchone()['count']
            print(f"  ✓ {emp_count} employees set with default 'employee' role")
        
        cursor.close()
        connection.close()
        
        print(f"✓ {db_name} migration completed")
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {db_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("Employee Role Column Migration")
    print("=" * 70)
    print("\nThis script will:")
    print("  • Add 'role' column to employees table if missing")
    print("  • Set default role as 'employee' for all employees without a role")
    print("  • Show role distribution in each database")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for db_name, db_config in DATABASES.items():
        if migrate_database(db_name, db_config):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print("Migration Summary")
    print("=" * 70)
    print(f"Total databases: {len(DATABASES)}")
    print(f"Successfully migrated: {success_count}")
    print(f"Failed: {fail_count}")
    print("=" * 70)
    
    if success_count == len(DATABASES):
        print("\n✓ All databases updated!")
        print("\nNext steps:")
        print("  1. Log out and log back in to refresh session with role")
        print("  2. Check Analytics menu - you should see Scheduled Reports and Audit Trail")
        print("  3. Use Manage Roles (/employee/manage_roles) to assign admin/manager roles")
        print("  4. Default role 'employee' has basic permissions")

if __name__ == '__main__':
    main()
