"""
Migration script to add analytics tables to existing tenant databases
Run this after implementing the analytics module to update fleet_twt and fleet_afroit databases
"""

import os
import sys
from tenant_manager import TenantDatabaseManager
from models_analytics import (
    CREATE_SCHEDULED_REPORTS_TABLE,
    CREATE_REPORT_TEMPLATES_TABLE,
    CREATE_KPI_SNAPSHOTS_TABLE,
    CREATE_REPORT_LOG_TABLE,
    CREATE_DASHBOARD_WIDGETS_TABLE
)

def migrate_tenant_analytics_tables(database_name):
    """Add analytics tables to a specific tenant database"""
    print(f"\n{'='*60}")
    print(f"Migrating analytics tables to: {database_name}")
    print(f"{'='*60}")
    
    try:
        conn = TenantDatabaseManager.get_tenant_connection(database_name)
        cursor = conn.cursor()
        
        tables = [
            ('scheduled_reports', CREATE_SCHEDULED_REPORTS_TABLE),
            ('report_templates', CREATE_REPORT_TEMPLATES_TABLE),
            ('kpi_snapshots', CREATE_KPI_SNAPSHOTS_TABLE),
            ('report_execution_log', CREATE_REPORT_LOG_TABLE),
            ('dashboard_widgets', CREATE_DASHBOARD_WIDGETS_TABLE)
        ]
        
        for table_name, create_sql in tables:
            try:
                # Check if table already exists
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if cursor.fetchone():
                    print(f"  ✓ Table '{table_name}' already exists - skipping")
                    continue
                
                # Create the table
                cursor.execute(create_sql)
                conn.commit()
                print(f"  ✓ Created table: {table_name}")
                
            except Exception as e:
                print(f"  ✗ Error creating table '{table_name}': {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Successfully migrated analytics tables to {database_name}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error migrating {database_name}: {e}")
        return False


def migrate_all_tenants():
    """Migrate analytics tables to all active tenant databases"""
    print("\n" + "="*60)
    print("ANALYTICS TABLES MIGRATION")
    print("="*60)
    print("This script will add analytics tables to existing tenant databases")
    print()
    
    # Get list of active companies from main database
    try:
        with TenantDatabaseManager.main_db() as main_conn:
            with main_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, subdomain, database_name, status
                    FROM companies
                    WHERE status IN ('active', 'trial')
                    ORDER BY name
                """)
                companies = cursor.fetchall()
                
                if not companies:
                    print("No active companies found to migrate")
                    return
                
                print(f"Found {len(companies)} active tenant(s) to migrate:\n")
                for company in companies:
                    print(f"  - {company['name']} ({company['subdomain']}) -> {company['database_name']}")
                
                print()
                response = input("Proceed with migration? (yes/no): ").lower()
                
                if response != 'yes':
                    print("Migration cancelled")
                    return
                
                print()
                success_count = 0
                fail_count = 0
                
                for company in companies:
                    if migrate_tenant_analytics_tables(company['database_name']):
                        success_count += 1
                    else:
                        fail_count += 1
                
                print("\n" + "="*60)
                print("MIGRATION SUMMARY")
                print("="*60)
                print(f"✓ Successful: {success_count}")
                print(f"✗ Failed: {fail_count}")
                print(f"Total: {len(companies)}")
                print()
                
    except Exception as e:
        print(f"\n✗ Error accessing main database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Enable multi-tenant mode
    os.environ['MULTI_TENANT_ENABLED'] = 'true'
    
    # Run migration for all tenants
    migrate_all_tenants()
