USE flask_auth_db;

-- Backup old data first
CREATE TABLE print_settings_backup SELECT * FROM print_settings;

-- Drop the old table
DROP TABLE print_settings;

-- Create the new table with setting_key/setting_value schema
CREATE TABLE print_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migrate old data to new schema
INSERT INTO print_settings (setting_key, setting_value, description) VALUES
('company_name', COALESCE((SELECT company_name FROM print_settings_backup LIMIT 1), 'Your Company Name'), 'Company name to display on printouts'),
('company_tagline', COALESCE((SELECT company_tagline FROM print_settings_backup LIMIT 1), 'Efficient Fleet Operations'), 'Company tagline'),
('company_address', COALESCE((SELECT company_address FROM print_settings_backup LIMIT 1), ''), 'Company address for printouts'),
('company_phone', COALESCE((SELECT company_phone FROM print_settings_backup LIMIT 1), ''), 'Company phone number'),
('company_email', COALESCE((SELECT company_email FROM print_settings_backup LIMIT 1), ''), 'Company email address'),
('company_website', COALESCE((SELECT company_website FROM print_settings_backup LIMIT 1), ''), 'Company website'),
('logo_path', COALESCE((SELECT logo_path FROM print_settings_backup LIMIT 1), ''), 'Company logo URL for printouts'),
('include_logo', '1', 'Include logo on printouts (1=yes, 0=no)'),
('footer_left', COALESCE((SELECT footer_left FROM print_settings_backup LIMIT 1), 'Printed by: {username}'), 'Footer left text'),
('footer_center', COALESCE((SELECT footer_center FROM print_settings_backup LIMIT 1), 'Page {page}'), 'Footer center text'),
('footer_right', COALESCE((SELECT footer_right FROM print_settings_backup LIMIT 1), 'Confidential Document'), 'Footer right text');
