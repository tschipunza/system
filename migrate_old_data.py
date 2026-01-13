"""
Migration Script: Move data from flask_auth_db to new tenant (twt)
This script creates a new company and migrates all existing data.
"""

import pymysql
from tenant_manager import TenantDatabaseManager
from models_tenant import Company
import sys

def migrate_old_data():
    """Migrate data from old flask_auth_db to new tenant database"""
    
    print("=" * 60)
    print("Migration: flask_auth_db -> twt tenant")
    print("=" * 60)
    
    # Configuration for new company
    company_config = {
        'name': 'twt',
        'subdomain': 'twt',
        'email': 'admin@twt.com',
        'phone': '',
        'plan': 'trial'
    }
    
    try:
        # Step 1: Check if company already exists
        print("\n1. Checking if company 'twt' exists...")
        with TenantDatabaseManager.main_db() as main_conn:
            with main_conn.cursor() as cursor:
                cursor.execute("SELECT * FROM companies WHERE subdomain = %s", (company_config['subdomain'],))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"   ✓ Company 'twt' already exists (ID: {existing['id']})")
                    company_id = existing['id']
                    database_name = existing['database_name']
                else:
                    # Step 2: Create new company
                    print("\n2. Creating company 'twt'...")
                    company_id = Company.create(
                        cursor=cursor,
                        name=company_config['name'],
                        subdomain=company_config['subdomain'],
                        email=company_config['email'],
                        phone=company_config['phone'],
                        plan=company_config['plan']
                    )
                    main_conn.commit()
                    
                    # Get the created company
                    cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
                    company = cursor.fetchone()
                    database_name = company['database_name']
                    print(f"   ✓ Company created: {company_config['name']} (ID: {company_id})")
                    print(f"   ✓ Database: {database_name}")
        
        # Step 3: Create tenant database if not exists
        print(f"\n3. Setting up tenant database '{database_name}'...")
        if not TenantDatabaseManager.create_tenant_database(database_name):
            print(f"   ✓ Database '{database_name}' already exists")
        else:
            print(f"   ✓ Database '{database_name}' created")
        
        # Step 4: Initialize schema
        print(f"\n4. Initializing database schema...")
        TenantDatabaseManager.initialize_tenant_schema(database_name)
        print(f"   ✓ Schema initialized")
        
        # Step 5: Connect to old database
        print("\n5. Connecting to old database (flask_auth_db)...")
        old_conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database='flask_auth_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        old_cursor = old_conn.cursor()
        print("   ✓ Connected to flask_auth_db")
        
        # Step 6: Connect to new tenant database
        print(f"\n6. Connecting to new tenant database ({database_name})...")
        new_conn = TenantDatabaseManager.get_tenant_connection(database_name)
        new_cursor = new_conn.cursor()
        print(f"   ✓ Connected to {database_name}")
        
        # Step 7: Migrate tables
        print("\n7. Migrating data...")
        
        # Tables to migrate in order (respecting foreign keys)
        tables = [
            'users',
            'employees', 
            'vehicles',
            'assignments',
            'fuel_records',
            'job_cards',
            'job_card_items',
            'service_maintenance',
            'requisitions',
            'system_settings'
        ]
        
        migration_summary = {}
        
        for table in tables:
            try:
                # Check if table exists in old database
                old_cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not old_cursor.fetchone():
                    print(f"   ⊘ Table '{table}' not found in old database, skipping")
                    migration_summary[table] = 0
                    continue
                
                # Get all data from old table
                old_cursor.execute(f"SELECT * FROM {table}")
                rows = old_cursor.fetchall()
                
                if not rows:
                    print(f"   ⊘ Table '{table}' is empty")
                    migration_summary[table] = 0
                    continue
                
                # Get column names
                old_cursor.execute(f"DESCRIBE {table}")
                columns = [col['Field'] for col in old_cursor.fetchall()]
                
                # Check if table exists in new database
                new_cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not new_cursor.fetchone():
                    print(f"   ⊘ Table '{table}' not found in new database, skipping")
                    migration_summary[table] = 0
                    continue
                
                # Verify columns match
                new_cursor.execute(f"DESCRIBE {table}")
                new_columns = [col['Field'] for col in new_cursor.fetchall()]
                
                # Use only common columns
                common_columns = [col for col in columns if col in new_columns]
                
                if not common_columns:
                    print(f"   ⚠ No matching columns for table '{table}', skipping")
                    migration_summary[table] = 0
                    continue
                
                # Insert data
                count = 0
                for row in rows:
                    try:
                        # Build INSERT query with only common columns
                        values = [row[col] for col in common_columns]
                        placeholders = ', '.join(['%s'] * len(common_columns))
                        column_names = ', '.join(common_columns)
                        
                        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                        new_cursor.execute(insert_query, values)
                        count += 1
                    except pymysql.err.IntegrityError as e:
                        # Skip duplicates (if primary key already exists)
                        if 'Duplicate entry' in str(e):
                            continue
                        else:
                            print(f"   ⚠ Error inserting row in {table}: {e}")
                            continue
                
                new_conn.commit()
                migration_summary[table] = count
                print(f"   ✓ Migrated {count} rows from '{table}'")
                
            except Exception as e:
                print(f"   ✗ Error migrating table '{table}': {e}")
                migration_summary[table] = 0
                continue
        
        # Step 8: Link admin user to tenant
        print("\n8. Linking admin users to tenant...")
        try:
            # Find admin users in the migrated employees
            new_cursor.execute("SELECT id, username, email FROM employees WHERE role = 'Administrator' LIMIT 1")
            admin = new_cursor.fetchone()
            
            if admin:
                with TenantDatabaseManager.main_db() as main_conn:
                    with main_conn.cursor() as cursor:
                        # Check if mapping already exists
                        cursor.execute(
                            "SELECT * FROM tenant_users WHERE company_id = %s AND user_id = %s AND user_type = 'employee'",
                            (company_id, admin['id'])
                        )
                        if not cursor.fetchone():
                            cursor.execute(
                                """INSERT INTO tenant_users 
                                (company_id, user_id, user_type, role, is_owner, status) 
                                VALUES (%s, %s, 'employee', 'administrator', 1, 'active')""",
                                (company_id, admin['id'])
                            )
                            main_conn.commit()
                            print(f"   ✓ Linked admin user '{admin['username']}' to company")
                        else:
                            print(f"   ✓ Admin user '{admin['username']}' already linked")
            else:
                print("   ⚠ No administrator found in employees table")
        except Exception as e:
            print(f"   ⚠ Error linking admin: {e}")
        
        # Step 9: Summary
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Company: {company_config['name']}")
        print(f"Subdomain: {company_config['subdomain']}")
        print(f"Database: {database_name}")
        print("\nRecords migrated:")
        total_records = 0
        for table, count in migration_summary.items():
            if count > 0:
                print(f"  - {table}: {count} records")
                total_records += count
        print(f"\nTotal: {total_records} records migrated")
        
        print("\n" + "=" * 60)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nYou can now login to 'twt' company using:")
        print(f"  - URL: http://localhost:5000/employee/login")
        print(f"  - Username: (your old username)")
        print(f"  - Password: (your old password)")
        
        # Close connections
        old_cursor.close()
        old_conn.close()
        new_cursor.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_old_data()
    sys.exit(0 if success else 1)
