#!/usr/bin/env python3
"""
Add notes column to service_requisitions table
"""
import pymysql

def add_notes_column():
    """Add notes column to service_requisitions table"""
    try:
        # Database configuration matching app.py
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ts#h3ph3rd',
            database='flask_auth_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        print("Adding notes column to service_requisitions table...")
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'flask_auth_db' 
            AND TABLE_NAME = 'service_requisitions' 
            AND COLUMN_NAME = 'notes'
        """)
        
        exists = cursor.fetchone()['COUNT(*)']
        
        if exists:
            print("✓ Column 'notes' already exists in service_requisitions table")
        else:
            cursor.execute("""
                ALTER TABLE service_requisitions 
                ADD COLUMN notes TEXT AFTER overall_status
            """)
            conn.commit()
            print("✓ Successfully added 'notes' column to service_requisitions table")
        
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add Notes Column")
    print("=" * 60)
    
    if add_notes_column():
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✗ Migration failed!")
