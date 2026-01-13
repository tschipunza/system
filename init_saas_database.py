"""
Initialize Multi-Tenant SaaS Database
Run this script once to set up the main database for multi-tenant architecture
"""

import sys
sys.path.append('.')

from tenant_manager import init_main_database, TenantDatabaseManager
from models_tenant import Company, TenantUser

def main():
    print("=" * 60)
    print("Fleet Manager SaaS - Database Initialization")
    print("=" * 60)
    print()
    
    print("This will create the main SaaS database structure:")
    print("  - companies table (tenant management)")
    print("  - tenant_users table (user-tenant mapping)")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Aborted.")
        return
    
    print()
    print("Initializing main database...")
    
    success = init_main_database()
    
    if success:
        print()
        print("=" * 60)
        print("✅ SaaS Database Initialized Successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Update app.py to use tenant middleware")
        print("2. Test company registration at /tenant/signup")
        print("3. Configure subdomain routing (DNS/hosts file)")
        print()
        print("Example hosts file entry for testing:")
        print("127.0.0.1  fleetmanager.local")
        print("127.0.0.1  acme.fleetmanager.local")
        print("127.0.0.1  demo.fleetmanager.local")
        print()
    else:
        print()
        print("❌ Initialization failed. Check the error messages above.")
        print()


if __name__ == '__main__':
    main()
