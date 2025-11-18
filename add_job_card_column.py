from app import app, get_db_connection

with app.app_context():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'service_maintenance' 
            AND COLUMN_NAME = 'job_card_id'
        """)
        exists = cursor.fetchone()['count']
        
        if exists == 0:
            print("Adding job_card_id column to service_maintenance table...")
            cursor.execute("""
                ALTER TABLE service_maintenance 
                ADD COLUMN job_card_id INT NULL AFTER performed_by
            """)
            cursor.execute("""
                ALTER TABLE service_maintenance 
                ADD FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE SET NULL
            """)
            conn.commit()
            print("✓ Column job_card_id added successfully!")
        else:
            print("✓ Column job_card_id already exists!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
