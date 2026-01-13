"""
Migration script to create print_settings table
Run this script to add the print_settings table to all databases
"""

import pymysql

def get_db_config(db_name):
    """Get database configuration for the specified database"""
    return {
        'host': 'localhost',
        'user': 'root',
        'password': 'ts#h3ph3rd',
        'database': db_name,
        'cursorclass': pymysql.cursors.DictCursor
    }

def create_print_settings_table(db_config, db_name):
    """Create print_settings table in the specified database"""
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # Check if table already exists
        cursor.execute("SHOW TABLES LIKE 'print_settings'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print(f"ℹ print_settings table already exists in {db_name}")
            
            # Check which structure it has
            cursor.execute("SHOW COLUMNS FROM print_settings LIKE 'setting_key'")
            has_setting_key = cursor.fetchone()
            
            if has_setting_key:
                print(f"  → Using new structure (setting_key)")
            else:
                print(f"  → Using legacy structure (company_name, etc.)")
                cursor.close()
                connection.close()
                return True
        
        # Create print_settings table (new structure)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS print_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) NOT NULL UNIQUE,
            setting_value TEXT,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_setting_key (setting_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_query)
        print(f"✓ Created print_settings table in {db_name}")
        
        # Insert default print settings
        default_settings = [
            ('company_name', 'Your Company Name', 'Company name to display on printouts'),
            ('company_address', 'Your Company Address', 'Company address for printouts'),
            ('company_phone', '', 'Company phone number'),
            ('company_email', '', 'Company email address'),
            ('logo_url', '', 'Company logo URL for printouts'),
            ('include_logo', '1', 'Include logo on printouts (1=yes, 0=no)'),
            ('paper_size', 'A4', 'Default paper size (A4, Letter, etc.)'),
            ('orientation', 'portrait', 'Default page orientation (portrait, landscape)'),
            ('margin_top', '20', 'Top margin in mm'),
            ('margin_bottom', '20', 'Bottom margin in mm'),
            ('margin_left', '15', 'Left margin in mm'),
            ('margin_right', '15', 'Right margin in mm'),
            ('font_size', '12', 'Default font size'),
            ('show_header', '1', 'Show header on printouts (1=yes, 0=no)'),
            ('show_footer', '1', 'Show footer on printouts (1=yes, 0=no)'),
            ('footer_text', 'Printed on {date}', 'Footer text template'),
            ('job_card_include_parts', '1', 'Include parts list on job cards'),
            ('job_card_include_labor', '1', 'Include labor costs on job cards'),
            ('job_card_include_signatures', '1', 'Include signature fields'),
            ('job_card_show_vehicle_details', '1', 'Show detailed vehicle information'),
        ]
        
        insert_query = """
        INSERT INTO print_settings (setting_key, setting_value, description)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            setting_value = VALUES(setting_value),
            description = VALUES(description)
        """
        
        cursor.executemany(insert_query, default_settings)
        connection.commit()
        print(f"✓ Inserted {len(default_settings)} default print settings")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating print_settings table in {db_name}: {str(e)}")
        return False

def main():
    """Run migration on all databases"""
    print("=" * 60)
    print("PRINT SETTINGS TABLE MIGRATION")
    print("=" * 60)
    print()
    
    databases = ['flask_auth_db', 'fleet_twt', 'fleet_afroit']
    success_count = 0
    
    for db_name in databases:
        print(f"\nProcessing database: {db_name}")
        print("-" * 60)
        
        db_config = get_db_config(db_name)
        if create_print_settings_table(db_config, db_name):
            success_count += 1
        
        print()
    
    print("=" * 60)
    print(f"Migration completed: {success_count}/{len(databases)} databases updated")
    print("=" * 60)
    
    if success_count == len(databases):
        print("✓ All databases migrated successfully!")
        return 0
    else:
        print("⚠ Some databases failed to migrate")
        return 1

if __name__ == '__main__':
    exit(main())
