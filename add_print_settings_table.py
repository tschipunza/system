#!/usr/bin/env python3
"""
Add print_settings table to database
"""
import pymysql

def add_print_settings_table():
    """Add print_settings table"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database='flask_auth_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        print("Creating print_settings table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS print_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255) DEFAULT 'Fleet Management System',
                company_tagline VARCHAR(255) DEFAULT 'Efficient Fleet Operations',
                company_address TEXT,
                company_phone VARCHAR(50),
                company_email VARCHAR(100),
                company_website VARCHAR(255),
                logo_path VARCHAR(255),
                footer_left VARCHAR(255) DEFAULT 'Printed by: {username}',
                footer_center VARCHAR(255) DEFAULT 'Page {page}',
                footer_right VARCHAR(255) DEFAULT 'Confidential Document',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                updated_by INT,
                FOREIGN KEY (updated_by) REFERENCES employees(id) ON DELETE SET NULL
            )
        """)
        
        # Check if there's already a record
        cursor.execute("SELECT COUNT(*) as count FROM print_settings")
        count = cursor.fetchone()['count']
        
        if count == 0:
            print("Inserting default print settings...")
            cursor.execute("""
                INSERT INTO print_settings (company_name, company_tagline) 
                VALUES ('Fleet Management System', 'Efficient Fleet Operations')
            """)
        
        conn.commit()
        print("✓ Successfully created print_settings table")
        
        cursor.close()
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add Print Settings Table")
    print("=" * 60)
    
    if add_print_settings_table():
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✗ Migration failed!")
