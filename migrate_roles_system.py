"""
Migration script to create roles, permissions, and role_permissions tables
for the complete role-based access control system
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

CREATE_PERMISSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    permission_name VARCHAR(200) NOT NULL,
    description TEXT,
    module VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_ROLES_TABLE = """
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_key VARCHAR(50) UNIQUE NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_ROLE_PERMISSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Default permissions organized by module
DEFAULT_PERMISSIONS = [
    # Vehicle Management
    ('view_vehicles', 'View Vehicles', 'Can view vehicle list and details', 'Vehicles'),
    ('add_vehicle', 'Add Vehicle', 'Can add new vehicles', 'Vehicles'),
    ('edit_vehicle', 'Edit Vehicle', 'Can edit vehicle details', 'Vehicles'),
    ('delete_vehicle', 'Delete Vehicle', 'Can delete vehicles', 'Vehicles'),
    
    # Vehicle Assignments
    ('view_assignments', 'View Assignments', 'Can view vehicle assignments', 'Assignments'),
    ('create_assignment', 'Create Assignment', 'Can assign vehicles to employees', 'Assignments'),
    ('edit_assignment', 'Edit Assignment', 'Can edit assignments', 'Assignments'),
    ('return_vehicle', 'Return Vehicle', 'Can process vehicle returns', 'Assignments'),
    ('view_own_assignments', 'View Own Assignments', 'Can view own vehicle assignments', 'Assignments'),
    
    # Fuel Management
    ('view_all_fuel_records', 'View All Fuel Records', 'Can view all fuel records', 'Fuel'),
    ('add_fuel_record', 'Add Fuel Record', 'Can add fuel records', 'Fuel'),
    ('edit_fuel_record', 'Edit Fuel Record', 'Can edit fuel records', 'Fuel'),
    ('delete_fuel_record', 'Delete Fuel Record', 'Can delete fuel records', 'Fuel'),
    ('view_own_fuel_records', 'View Own Fuel Records', 'Can view own fuel records', 'Fuel'),
    
    # Service & Maintenance
    ('view_service_records', 'View Service Records', 'Can view service records', 'Service'),
    ('add_service_record', 'Add Service Record', 'Can add service records', 'Service'),
    ('edit_service_record', 'Edit Service Record', 'Can edit service records', 'Service'),
    ('delete_service_record', 'Delete Service Record', 'Can delete service records', 'Service'),
    ('view_service_notifications', 'View Service Notifications', 'Can view service notifications', 'Service'),
    
    # Job Cards
    ('view_job_cards', 'View Job Cards', 'Can view job cards', 'Job Cards'),
    ('create_job_card', 'Create Job Card', 'Can create job cards', 'Job Cards'),
    ('edit_job_card', 'Edit Job Card', 'Can edit job cards', 'Job Cards'),
    ('delete_job_card', 'Delete Job Card', 'Can delete job cards', 'Job Cards'),
    
    # Service Requisitions
    ('view_requisitions', 'View Requisitions', 'Can view service requisitions', 'Requisitions'),
    ('create_requisition', 'Create Requisition', 'Can create service requisitions', 'Requisitions'),
    ('review_requisition', 'Review Requisition', 'Can review requisitions (Line Manager)', 'Requisitions'),
    ('approve_requisition', 'Approve Requisition', 'Can approve requisitions (Director)', 'Requisitions'),
    
    # Employee Management
    ('view_employees', 'View Employees', 'Can view employee list', 'Employees'),
    ('add_employee', 'Add Employee', 'Can add new employees', 'Employees'),
    ('edit_employee', 'Edit Employee', 'Can edit employee details', 'Employees'),
    ('delete_employee', 'Delete Employee', 'Can delete employees', 'Employees'),
    ('manage_roles', 'Manage Roles', 'Can manage roles and permissions', 'Employees'),
    
    # Settings
    ('view_settings', 'View Settings', 'Can view system settings', 'Settings'),
    ('edit_settings', 'Edit Settings', 'Can edit system settings', 'Settings'),
    ('manage_backups', 'Manage Backups', 'Can manage database backups', 'Settings'),
    ('view_notifications_settings', 'View Notification Settings', 'Can view notification settings', 'Settings'),
    ('edit_notifications_settings', 'Edit Notification Settings', 'Can edit notification settings', 'Settings'),
    
    # Reports
    ('view_reports', 'View Reports', 'Can view reports and analytics', 'Reports'),
    ('export_reports', 'Export Reports', 'Can export reports', 'Reports'),
]

# Default roles with their permissions
DEFAULT_ROLES = {
    'employee': {
        'name': 'Employee',
        'description': 'Basic employee with limited access',
        'is_system': True,
        'permissions': [
            'view_vehicles', 'view_own_assignments', 'view_own_fuel_records',
            'add_fuel_record', 'create_requisition', 'view_requisitions'
        ]
    },
    'manager': {
        'name': 'Manager',
        'description': 'Line manager who can review requisitions',
        'is_system': True,
        'permissions': [
            'view_vehicles', 'view_assignments', 'create_assignment', 'return_vehicle',
            'view_all_fuel_records', 'add_fuel_record', 'view_service_records',
            'view_service_notifications', 'view_job_cards', 'view_requisitions',
            'create_requisition', 'review_requisition', 'view_reports'
        ]
    },
    'director': {
        'name': 'Director',
        'description': 'Director who can approve requisitions and access most features',
        'is_system': True,
        'permissions': [
            'view_vehicles', 'add_vehicle', 'edit_vehicle', 'view_assignments',
            'create_assignment', 'edit_assignment', 'return_vehicle',
            'view_all_fuel_records', 'add_fuel_record', 'view_service_records',
            'add_service_record', 'view_service_notifications', 'view_job_cards',
            'create_job_card', 'view_requisitions', 'create_requisition',
            'review_requisition', 'approve_requisition', 'view_reports',
            'export_reports', 'view_settings'
        ]
    },
    'admin': {
        'name': 'Administrator',
        'description': 'Full system access with all permissions',
        'is_system': True,
        'permissions': 'all'  # All permissions
    }
}

def migrate_database(db_name, db_config):
    """Migrate a single database"""
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        print(f"\n🔧 Migrating {db_name}...")
        
        # Create tables
        print("  Creating permissions table...")
        cursor.execute(CREATE_PERMISSIONS_TABLE)
        
        print("  Creating roles table...")
        cursor.execute(CREATE_ROLES_TABLE)
        
        print("  Creating role_permissions table...")
        cursor.execute(CREATE_ROLE_PERMISSIONS_TABLE)
        
        connection.commit()
        print("  ✓ Tables created successfully")
        
        # Insert default permissions
        print("\n  Inserting default permissions...")
        perm_count = 0
        for perm_key, perm_name, description, module in DEFAULT_PERMISSIONS:
            cursor.execute("""
                INSERT INTO permissions (permission_key, permission_name, description, module)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    permission_name = VALUES(permission_name),
                    description = VALUES(description),
                    module = VALUES(module)
            """, (perm_key, perm_name, description, module))
            perm_count += 1
        
        connection.commit()
        print(f"  ✓ {perm_count} permissions inserted")
        
        # Insert default roles
        print("\n  Inserting default roles...")
        role_count = 0
        for role_key, role_data in DEFAULT_ROLES.items():
            cursor.execute("""
                INSERT INTO roles (role_key, role_name, description, is_system_role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    role_name = VALUES(role_name),
                    description = VALUES(description)
            """, (role_key, role_data['name'], role_data['description'], role_data['is_system']))
            
            # Get role ID
            cursor.execute("SELECT id FROM roles WHERE role_key = %s", (role_key,))
            role = cursor.fetchone()
            if role:
                role_id = role['id']
                
                # Assign permissions
                if role_data['permissions'] == 'all':
                    # Admin gets all permissions
                    cursor.execute("SELECT id FROM permissions")
                    all_permissions = cursor.fetchall()
                    for perm in all_permissions:
                        cursor.execute("""
                            INSERT IGNORE INTO role_permissions (role_id, permission_id)
                            VALUES (%s, %s)
                        """, (role_id, perm['id']))
                    print(f"    ✓ {role_data['name']} (all {len(all_permissions)} permissions)")
                else:
                    # Assign specific permissions
                    for perm_key in role_data['permissions']:
                        cursor.execute("SELECT id FROM permissions WHERE permission_key = %s", (perm_key,))
                        perm = cursor.fetchone()
                        if perm:
                            cursor.execute("""
                                INSERT IGNORE INTO role_permissions (role_id, permission_id)
                                VALUES (%s, %s)
                            """, (role_id, perm['id']))
                    print(f"    ✓ {role_data['name']} ({len(role_data['permissions'])} permissions)")
                
                role_count += 1
        
        connection.commit()
        print(f"  ✓ {role_count} roles created with permissions")
        
        # Update existing employees with roles if they don't have one
        print("\n  Updating employee roles...")
        cursor.execute("SHOW COLUMNS FROM employees LIKE 'role'")
        if cursor.fetchone():
            cursor.execute("SELECT id, role FROM employees")
            employees = cursor.fetchall()
            updated_count = 0
            for emp in employees:
                if not emp['role'] or emp['role'] in ['NULL', '']:
                    cursor.execute("UPDATE employees SET role = 'employee' WHERE id = %s", (emp['id'],))
                    updated_count += 1
            
            connection.commit()
            if updated_count > 0:
                print(f"  ✓ Updated {updated_count} employees with default role")
            else:
                print("  ✓ All employees already have roles")
        else:
            print("  ℹ Skipping employee role update (role column not found)")
        
        cursor.close()
        connection.close()
        
        print(f"\n✓ {db_name} migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error migrating {db_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("Roles and Permissions System Migration")
    print("=" * 70)
    print("\nThis script will create:")
    print("  • roles table")
    print("  • permissions table")
    print("  • role_permissions table")
    print("\nAnd populate with:")
    print(f"  • {len(DEFAULT_PERMISSIONS)} default permissions")
    print(f"  • {len(DEFAULT_ROLES)} default roles (employee, manager, director, admin)")
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
        print("\n✓ Roles and permissions system enabled!")
        print("\nDefault Roles:")
        print("  • Employee: Basic access (view vehicles, own assignments, fuel records)")
        print("  • Manager: Team management (assignments, fuel records, requisitions)")
        print("  • Director: Advanced access (approvals, most features)")
        print("  • Admin: Full system access (all permissions)")
        print("\nNext steps:")
        print("  1. Assign roles to employees in the Manage Roles interface")
        print("  2. Test permissions by logging in with different role types")
        print("  3. Customize permissions as needed for your organization")

if __name__ == '__main__':
    main()
