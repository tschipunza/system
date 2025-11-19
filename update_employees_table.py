from app import get_db_connection

def update_employees_table():
    """Add new columns to employees table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Add role column
        try:
            cursor.execute("ALTER TABLE employees ADD COLUMN role VARCHAR(50) DEFAULT 'employee'")
            print("✓ Added 'role' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("- 'role' column already exists")
            else:
                print(f"Error adding 'role' column: {e}")
        
        # Add status column
        try:
            cursor.execute("ALTER TABLE employees ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            print("✓ Added 'status' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("- 'status' column already exists")
            else:
                print(f"Error adding 'status' column: {e}")
        
        # Add phone column
        try:
            cursor.execute("ALTER TABLE employees ADD COLUMN phone VARCHAR(20)")
            print("✓ Added 'phone' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("- 'phone' column already exists")
            else:
                print(f"Error adding 'phone' column: {e}")
        
        # Add updated_at column
        try:
            cursor.execute("ALTER TABLE employees ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            print("✓ Added 'updated_at' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("- 'updated_at' column already exists")
            else:
                print(f"Error adding 'updated_at' column: {e}")
        
        conn.commit()
        print("\n✓ Database update completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_employees_table()
