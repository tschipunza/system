"""
Add New Permissions to Existing Roles
Use this script when you add new modules or features to the system
"""
from app import get_db_connection

def add_new_permissions(permissions_list):
    """
    Add new permissions to the system
    
    Args:
        permissions_list: List of tuples (permission_key, permission_name, description, module)
    
    Example:
        add_new_permissions([
            ('view_reports', 'View Reports', 'Can view analytics reports', 'Reports'),
            ('export_reports', 'Export Reports', 'Can export reports to PDF/Excel', 'Reports')
        ])
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        added_count = 0
        updated_count = 0
        
        print("\n" + "="*60)
        print("ADDING NEW PERMISSIONS")
        print("="*60)
        
        for perm_key, perm_name, description, module in permissions_list:
            try:
                # Check if permission already exists
                cursor.execute("SELECT id FROM permissions WHERE permission_key = %s", (perm_key,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE permissions 
                        SET permission_name = %s, description = %s, module = %s
                        WHERE permission_key = %s
                    """, (perm_name, description, module, perm_key))
                    print(f"  ↻ Updated: {perm_name}")
                    updated_count += 1
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO permissions (permission_key, permission_name, description, module)
                        VALUES (%s, %s, %s, %s)
                    """, (perm_key, perm_name, description, module))
                    print(f"  ✓ Added: {perm_name}")
                    added_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error with {perm_name}: {e}")
        
        conn.commit()
        
        print("\n" + "="*60)
        print(f"Summary: {added_count} added, {updated_count} updated")
        print("="*60)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def assign_permissions_to_role(role_key, permission_keys):
    """
    Assign additional permissions to an existing role
    
    Args:
        role_key: The role key (e.g., 'admin', 'manager')
        permission_keys: List of permission keys to add
    
    Example:
        assign_permissions_to_role('manager', ['view_reports', 'export_reports'])
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get role ID
        cursor.execute("SELECT id, role_name FROM roles WHERE role_key = %s", (role_key,))
        role = cursor.fetchone()
        
        if not role:
            print(f"❌ Role '{role_key}' not found!")
            return False
        
        print(f"\n{'='*60}")
        print(f"ASSIGNING PERMISSIONS TO: {role['role_name']}")
        print("="*60)
        
        assigned_count = 0
        already_exists = 0
        
        for perm_key in permission_keys:
            # Get permission ID
            cursor.execute("SELECT id, permission_name FROM permissions WHERE permission_key = %s", (perm_key,))
            perm = cursor.fetchone()
            
            if not perm:
                print(f"  ✗ Permission '{perm_key}' not found!")
                continue
            
            # Check if already assigned
            cursor.execute("""
                SELECT id FROM role_permissions 
                WHERE role_id = %s AND permission_id = %s
            """, (role['id'], perm['id']))
            
            if cursor.fetchone():
                print(f"  - Already has: {perm['permission_name']}")
                already_exists += 1
            else:
                # Assign permission
                cursor.execute("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (%s, %s)
                """, (role['id'], perm['id']))
                print(f"  ✓ Assigned: {perm['permission_name']}")
                assigned_count += 1
        
        conn.commit()
        
        print("\n" + "="*60)
        print(f"Summary: {assigned_count} assigned, {already_exists} already existed")
        print("="*60)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def bulk_assign_permissions_to_roles(permissions_by_role):
    """
    Assign permissions to multiple roles at once
    
    Args:
        permissions_by_role: Dict mapping role_key to list of permission_keys
    
    Example:
        bulk_assign_permissions_to_roles({
            'manager': ['view_reports'],
            'director': ['view_reports', 'export_reports'],
            'admin': ['view_reports', 'export_reports']
        })
    """
    for role_key, permission_keys in permissions_by_role.items():
        assign_permissions_to_role(role_key, permission_keys)
        print()


# =============================================================================
# EXAMPLE: Add new module permissions
# =============================================================================

# Example 1: Adding Inventory Management Module
INVENTORY_PERMISSIONS = [
    ('view_inventory', 'View Inventory', 'Can view inventory items', 'Inventory'),
    ('add_inventory_item', 'Add Inventory Item', 'Can add new inventory items', 'Inventory'),
    ('edit_inventory_item', 'Edit Inventory Item', 'Can edit inventory items', 'Inventory'),
    ('delete_inventory_item', 'Delete Inventory Item', 'Can delete inventory items', 'Inventory'),
    ('view_stock_levels', 'View Stock Levels', 'Can view stock level reports', 'Inventory'),
    ('manage_suppliers', 'Manage Suppliers', 'Can manage supplier information', 'Inventory'),
]

# Example 2: Adding Advanced Reporting Module
REPORTING_PERMISSIONS = [
    ('view_advanced_reports', 'View Advanced Reports', 'Can view detailed analytics', 'Advanced Reports'),
    ('create_custom_reports', 'Create Custom Reports', 'Can create custom report templates', 'Advanced Reports'),
    ('schedule_reports', 'Schedule Reports', 'Can schedule automated reports', 'Advanced Reports'),
    ('share_reports', 'Share Reports', 'Can share reports with others', 'Advanced Reports'),
]

# Example 3: Adding Fleet Tracking Module
TRACKING_PERMISSIONS = [
    ('view_gps_tracking', 'View GPS Tracking', 'Can view real-time vehicle locations', 'GPS Tracking'),
    ('view_route_history', 'View Route History', 'Can view historical routes', 'GPS Tracking'),
    ('set_geofences', 'Set Geofences', 'Can create and manage geofences', 'GPS Tracking'),
    ('receive_tracking_alerts', 'Receive Tracking Alerts', 'Can receive location-based alerts', 'GPS Tracking'),
]


def example_add_inventory_module():
    """Example: Add inventory management permissions"""
    print("\n🔧 Adding Inventory Management Module...")
    
    # Step 1: Add the permissions
    if add_new_permissions(INVENTORY_PERMISSIONS):
        
        # Step 2: Assign to roles based on their level
        print("\n🔧 Assigning permissions to roles...")
        bulk_assign_permissions_to_roles({
            'employee': ['view_inventory'],  # Employees can only view
            'manager': ['view_inventory', 'view_stock_levels'],  # Managers can view and check stock
            'director': ['view_inventory', 'add_inventory_item', 'edit_inventory_item', 'view_stock_levels'],  # Directors can add/edit
            'admin': ['view_inventory', 'add_inventory_item', 'edit_inventory_item', 'delete_inventory_item', 'view_stock_levels', 'manage_suppliers']  # Admin gets all
        })
        
        print("\n✅ Inventory module permissions added successfully!")


def example_add_reporting_module():
    """Example: Add advanced reporting permissions"""
    print("\n🔧 Adding Advanced Reporting Module...")
    
    if add_new_permissions(REPORTING_PERMISSIONS):
        bulk_assign_permissions_to_roles({
            'manager': ['view_advanced_reports'],
            'director': ['view_advanced_reports', 'create_custom_reports', 'share_reports'],
            'admin': ['view_advanced_reports', 'create_custom_reports', 'schedule_reports', 'share_reports']
        })
        
        print("\n✅ Advanced reporting permissions added successfully!")


def example_add_tracking_module():
    """Example: Add GPS tracking permissions"""
    print("\n🔧 Adding GPS Tracking Module...")
    
    if add_new_permissions(TRACKING_PERMISSIONS):
        bulk_assign_permissions_to_roles({
            'employee': ['view_gps_tracking'],
            'manager': ['view_gps_tracking', 'view_route_history', 'receive_tracking_alerts'],
            'director': ['view_gps_tracking', 'view_route_history', 'set_geofences', 'receive_tracking_alerts'],
            'admin': ['view_gps_tracking', 'view_route_history', 'set_geofences', 'receive_tracking_alerts']
        })
        
        print("\n✅ GPS tracking permissions added successfully!")


# =============================================================================
# INTERACTIVE MENU
# =============================================================================

def main_menu():
    """Interactive menu for adding permissions"""
    while True:
        print("\n" + "="*60)
        print("ADD NEW PERMISSIONS TO SYSTEM")
        print("="*60)
        print("\nExamples:")
        print("  1. Add Inventory Management Module")
        print("  2. Add Advanced Reporting Module")
        print("  3. Add GPS Tracking Module")
        print("\nCustom:")
        print("  4. Add Custom Permissions")
        print("  5. Assign Permissions to Role")
        print("\n  0. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            example_add_inventory_module()
        elif choice == '2':
            example_add_reporting_module()
        elif choice == '3':
            example_add_tracking_module()
        elif choice == '4':
            add_custom_permissions_interactive()
        elif choice == '5':
            assign_permissions_interactive()
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice!")


def add_custom_permissions_interactive():
    """Interactive way to add custom permissions"""
    print("\n" + "="*60)
    print("ADD CUSTOM PERMISSIONS")
    print("="*60)
    
    permissions = []
    
    while True:
        print("\nEnter permission details (or press Enter to finish):")
        perm_key = input("  Permission Key (e.g., view_reports): ").strip()
        
        if not perm_key:
            break
        
        perm_name = input("  Permission Name (e.g., View Reports): ").strip()
        description = input("  Description: ").strip()
        module = input("  Module (e.g., Reports): ").strip()
        
        permissions.append((perm_key, perm_name, description, module))
        print(f"  ✓ Added to queue: {perm_name}")
    
    if permissions:
        print(f"\n📋 Total permissions to add: {len(permissions)}")
        confirm = input("Proceed? (y/n): ").strip().lower()
        
        if confirm == 'y':
            add_new_permissions(permissions)
        else:
            print("❌ Cancelled")
    else:
        print("❌ No permissions added")


def assign_permissions_interactive():
    """Interactive way to assign permissions to a role"""
    print("\n" + "="*60)
    print("ASSIGN PERMISSIONS TO ROLE")
    print("="*60)
    
    # Show available roles
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role_key, role_name FROM roles ORDER BY role_name")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print("\nAvailable Roles:")
    for role in roles:
        print(f"  - {role['role_key']}: {role['role_name']}")
    
    role_key = input("\nEnter role key: ").strip()
    
    # Show available permissions
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT permission_key, permission_name, module FROM permissions ORDER BY module, permission_name")
    perms = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print("\nAvailable Permissions:")
    current_module = None
    for perm in perms:
        if perm['module'] != current_module:
            current_module = perm['module']
            print(f"\n{current_module}:")
        print(f"  - {perm['permission_key']}: {perm['permission_name']}")
    
    print("\nEnter permission keys (comma-separated):")
    perm_input = input("> ").strip()
    permission_keys = [p.strip() for p in perm_input.split(',') if p.strip()]
    
    if permission_keys:
        assign_permissions_to_role(role_key, permission_keys)
    else:
        print("❌ No permissions specified")


if __name__ == '__main__':
    main_menu()
