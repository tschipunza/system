"""
Check user permissions for debugging
"""
import pymysql
import sys

username = sys.argv[1] if len(sys.argv) > 1 else 'tschipunza'

DATABASES = ['fleet_twt', 'fleet_afroit', 'flask_auth_db']

for db_name in DATABASES:
    print(f"\n{'='*70}")
    print(f"Database: {db_name}")
    print('='*70)
    
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Get employee info
        cursor.execute('SELECT id, username, email, role FROM employees WHERE username = %s', (username,))
        employee = cursor.fetchone()
        
        if not employee:
            print(f"❌ User '{username}' not found in {db_name}")
            conn.close()
            continue
        
        print(f"✅ User found:")
        print(f"   ID: {employee['id']}")
        print(f"   Username: {employee['username']}")
        print(f"   Email: {employee['email']}")
        print(f"   Role: {employee['role']}")
        
        # Get permissions from new role system
        cursor.execute('''
            SELECT p.permission_key, p.permission_name, p.module
            FROM permissions p
            INNER JOIN role_permissions rp ON p.id = rp.permission_id
            INNER JOIN roles r ON r.id = rp.role_id
            WHERE r.role_key = %s
            ORDER BY p.module, p.permission_name
        ''', (employee['role'],))
        
        perms = cursor.fetchall()
        
        if perms:
            print(f"\n📋 Role System Permissions ({len(perms)}):")
            current_module = None
            for p in perms:
                if p['module'] != current_module:
                    current_module = p['module']
                    print(f"\n   {current_module}:")
                print(f"     • {p['permission_key']} - {p['permission_name']}")
        else:
            print(f"\n⚠️  No permissions found in role system for role '{employee['role']}'")
            
            # Check available roles
            cursor.execute('SELECT role_key, role_name FROM roles')
            available_roles = cursor.fetchall()
            print(f"\n   Available roles in database:")
            for r in available_roles:
                print(f"     • {r['role_key']} ({r['role_name']})")
        
        # Get analytics permissions
        cursor.execute('SELECT permission FROM analytics_permissions WHERE role = %s', (employee['role'],))
        aperms = cursor.fetchall()
        
        if aperms:
            print(f"\n📊 Analytics Permissions ({len(aperms)}):")
            for p in aperms:
                print(f"   • {p['permission']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking {db_name}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*70}")
print("Recommendation:")
print("If no permissions found, update user role to match available roles:")
print("  UPDATE employees SET role = 'admin' WHERE username = 'tschipunza';")
print('='*70)
