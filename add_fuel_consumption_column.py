"""
Add expected_fuel_consumption column to vehicles table
"""
from app import get_db_connection

def add_fuel_consumption_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'flask_auth_db' 
            AND TABLE_NAME = 'vehicles' 
            AND COLUMN_NAME = 'expected_fuel_consumption'
        """)
        result = cursor.fetchone()
        
        if result['count'] == 0:
            # Add the column
            cursor.execute("""
                ALTER TABLE vehicles 
                ADD COLUMN expected_fuel_consumption DECIMAL(5,2) 
                COMMENT 'Expected km per liter' 
                AFTER last_service_date
            """)
            conn.commit()
            print("✓ Successfully added expected_fuel_consumption column to vehicles table")
        else:
            print("✓ expected_fuel_consumption column already exists")
        
        # Add default threshold setting if not exists
        cursor.execute("""
            INSERT IGNORE INTO system_settings (setting_key, setting_value, description, category)
            VALUES ('default_fuel_consumption_threshold', '18', 'Default fuel consumption threshold (km per liter) for vehicles without specific consumption set', 'fuel')
        """)
        conn.commit()
        print("✓ Added default fuel consumption threshold setting")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    add_fuel_consumption_column()
