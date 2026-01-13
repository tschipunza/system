"""
Script to assign analytics permissions to roles
Run this to give specific roles access to analytics features
"""
import pymysql
import sys

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

# Analytics permissions by role
ROLE_PERMISSIONS = {
    'admin': [
        'view_dashboard',
        'view_all_reports',
        'view_kpis',
        'export_excel',
        'export_pdf',
        'create_scheduled_reports',
        'delete_scheduled_reports',
        'view_audit_trail',
        'manage_permissions'
    ],
    'director': [
        'view_dashboard',
        'view_all_reports',
        'view_kpis',
        'export_excel',
        'export_pdf',
        'create_scheduled_reports',
        'view_audit_trail'
    ],
    'manager': [
        'view_dashboard',
        'view_team_reports',
        'view_kpis',
        'export_excel',
        'create_scheduled_reports'
    ],
    'employee': [
        'view_dashboard',
        'view_own_reports',
        'export_excel'
    ]
}

def assign_permissions(db_name, db_config, role_name=None):
    """Assign analytics permissions to roles"""
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print(f"\n{'='*70}")
        print(f"Database: {db_name}")
        print('='*70)
        
        # Get roles to update
        if role_name:
            roles_to_update = {role_name: ROLE_PERMISSIONS.get(role_name, [])}
        else:
            roles_to_update = ROLE_PERMISSIONS
        
        for role, permissions in roles_to_update.items():
            print(f"\n🔧 Updating role: {role}")
            
            # Delete existing analytics permissions for this role
            deleted = cursor.execute(
                "DELETE FROM analytics_permissions WHERE role = %s",
                (role,)
            )
            print(f"  Removed {deleted} existing permissions")
            
            # Insert new permissions
            inserted = 0
            for permission in permissions:
                try:
                    cursor.execute("""
                        INSERT INTO analytics_permissions (role, permission, description)
                        VALUES (%s, %s, %s)
                    """, (role, permission, f"Access to {permission.replace('_', ' ')}"))
                    inserted += 1
                except Exception as e:
                    if "Duplicate entry" not in str(e):
                        print(f"    ⚠️  Error adding {permission}: {e}")
            
            conn.commit()
            print(f"  ✅ Added {inserted} permissions")
            
            # Show current permissions
            cursor.execute(
                "SELECT permission FROM analytics_permissions WHERE role = %s ORDER BY permission",
                (role,)
            )
            current = cursor.fetchall()
            print(f"  Current permissions ({len(current)}):")
            for p in current:
                print(f"    • {p['permission']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ {db_name} updated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error updating {db_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_current_permissions(db_name, db_config):
    """Show current analytics permissions"""
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print(f"\n{'='*70}")
        print(f"Current Analytics Permissions - {db_name}")
        print('='*70)
        
        cursor.execute("""
            SELECT role, GROUP_CONCAT(permission ORDER BY permission SEPARATOR ', ') as permissions
            FROM analytics_permissions
            GROUP BY role
            ORDER BY role
        """)
        
        roles = cursor.fetchall()
        
        if roles:
            for role in roles:
                print(f"\n{role['role'].upper()}:")
                perms = role['permissions'].split(', ')
                for p in perms:
                    print(f"  • {p}")
        else:
            print("\n⚠️  No analytics permissions found!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Assign analytics permissions to roles')
    parser.add_argument('--role', choices=['admin', 'director', 'manager', 'employee'], 
                       help='Specific role to update (default: all roles)')
    parser.add_argument('--show', action='store_true',
                       help='Show current permissions only')
    
    args = parser.parse_args()
    
    if args.show:
        # Show current permissions
        for db_name, db_config in DATABASES.items():
            show_current_permissions(db_name, db_config)
        return
    
    # Assign permissions
    print("="*70)
    print("Analytics Permissions Assignment")
    print("="*70)
    
    if args.role:
        print(f"\nAssigning permissions for role: {args.role}")
        print(f"Permissions: {', '.join(ROLE_PERMISSIONS.get(args.role, []))}")
    else:
        print("\nAssigning permissions for all roles:")
        for role, perms in ROLE_PERMISSIONS.items():
            print(f"  • {role}: {len(perms)} permissions")
    
    print("\nThis will update:")
    print("  • view_audit_trail (admin, director)")
    print("  • create_scheduled_reports (admin, director, manager)")
    print("  • view_kpis (admin, director, manager)")
    print("  • view_dashboard (all roles)")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    success_count = 0
    fail_count = 0
    
    for db_name, db_config in DATABASES.items():
        if assign_permissions(db_name, db_config, args.role):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"Databases updated: {success_count}/{len(DATABASES)}")
    print(f"Failed: {fail_count}")
    
    if success_count > 0:
        print("\n✅ Permissions updated!")
        print("\nNext steps:")
        print("  1. Users must log out and log back in")
        print("  2. Check Analytics menu - items should now be visible")
        print("  3. Run with --show to verify permissions")
        print("\nTo show current permissions:")
        print("  python assign_analytics_permissions.py --show")
        print("\nTo update a specific role:")
        print("  python assign_analytics_permissions.py --role manager")

if __name__ == '__main__':
    main()
