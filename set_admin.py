from app import get_db_connection

def set_admin_role():
    """Set admin role for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Show all employees
        cursor.execute("SELECT id, employee_id, username, email, role FROM employees")
        employees = cursor.fetchall()
        
        print("\n=== Current Employees ===")
        for emp in employees:
            print(f"ID: {emp['id']}, Employee ID: {emp['employee_id']}, Username: {emp['username']}, Role: {emp['role']}")
        
        # Get user input
        print("\n" + "="*50)
        user_input = input("Enter the ID or username of employee to make admin: ")
        
        # Try to find by ID first, then username
        if user_input.isdigit():
            cursor.execute("SELECT * FROM employees WHERE id = %s", (int(user_input),))
        else:
            cursor.execute("SELECT * FROM employees WHERE username = %s", (user_input,))
        
        employee = cursor.fetchone()
        
        if not employee:
            print("❌ Employee not found!")
            return
        
        # Update role to admin
        cursor.execute("UPDATE employees SET role = 'admin' WHERE id = %s", (employee['id'],))
        conn.commit()
        
        print(f"\n✓ Successfully set {employee['username']} (ID: {employee['employee_id']}) as ADMIN!")
        print(f"  Email: {employee['email']}")
        print(f"  Previous Role: {employee['role']}")
        print(f"  New Role: admin")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    set_admin_role()
