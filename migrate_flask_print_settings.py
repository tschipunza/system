#!/usr/bin/env python3
import pymysql

def migrate_print_settings():
    """Migrate flask_auth_db print_settings table to new schema"""
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='ts#h3ph3rd',
        database='flask_auth_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    try:
        print("Starting migration...")
        
        # Get old data before dropping
        cursor.execute("SELECT * FROM print_settings LIMIT 1")
        old_data = cursor.fetchone()
        
        # Backup old table
        cursor.execute("CREATE TABLE IF NOT EXISTS print_settings_backup_old LIKE print_settings")
        cursor.execute("INSERT INTO print_settings_backup_old SELECT * FROM print_settings")
        print("✓ Backed up old table as print_settings_backup_old")
        
        # Drop old table
        cursor.execute("DROP TABLE print_settings")
        print("✓ Dropped old print_settings table")
        
        # Create new table with key-value schema
        cursor.execute("""
            CREATE TABLE print_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) NOT NULL UNIQUE,
                setting_value TEXT,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_setting_key (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Created new print_settings table with key-value schema")
        
        # Migrate data if it exists
        if old_data:
            # Insert migrated settings
            settings_data = [
                ('company_name', old_data.get('company_name', 'Your Company Name'), 'Company name to display on printouts'),
                ('company_tagline', old_data.get('company_tagline', 'Efficient Fleet Operations'), 'Company tagline'),
                ('company_address', old_data.get('company_address', ''), 'Company address for printouts'),
                ('company_phone', old_data.get('company_phone', ''), 'Company phone number'),
                ('company_email', old_data.get('company_email', ''), 'Company email address'),
                ('company_website', old_data.get('company_website', ''), 'Company website'),
                ('logo_path', old_data.get('logo_path', ''), 'Company logo URL for printouts'),
                ('include_logo', '1', 'Include logo on printouts (1=yes, 0=no)'),
                ('footer_left', old_data.get('footer_left', 'Printed by: {username}'), 'Footer left text'),
                ('footer_center', old_data.get('footer_center', 'Page {page}'), 'Footer center text'),
                ('footer_right', old_data.get('footer_right', 'Confidential Document'), 'Footer right text'),
            ]
            
            for setting_key, setting_value, description in settings_data:
                cursor.execute("""
                    INSERT INTO print_settings (setting_key, setting_value, description)
                    VALUES (%s, %s, %s)
                """, (setting_key, setting_value, description))
            
            print(f"✓ Migrated {len(settings_data)} settings to new schema")
        else:
            # If no data, insert defaults
            default_settings = [
                ('company_name', 'Your Company Name', 'Company name to display on printouts'),
                ('company_tagline', 'Efficient Fleet Operations', 'Company tagline'),
                ('company_address', '', 'Company address for printouts'),
                ('company_phone', '', 'Company phone number'),
                ('company_email', '', 'Company email address'),
                ('company_website', '', 'Company website'),
                ('logo_path', '', 'Company logo URL for printouts'),
                ('include_logo', '1', 'Include logo on printouts (1=yes, 0=no)'),
                ('footer_left', 'Printed by: {username}', 'Footer left text'),
                ('footer_center', 'Page {page}', 'Footer center text'),
                ('footer_right', 'Confidential Document', 'Footer right text'),
            ]
            
            for setting_key, setting_value, description in default_settings:
                cursor.execute("""
                    INSERT INTO print_settings (setting_key, setting_value, description)
                    VALUES (%s, %s, %s)
                """, (setting_key, setting_value, description))
            
            print(f"✓ Inserted default settings")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("The print_settings table has been migrated to the new key-value schema")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True

if __name__ == '__main__':
    migrate_print_settings()
