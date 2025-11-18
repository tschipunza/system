# Settings and Configuration Tables

CREATE_SYSTEM_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    category VARCHAR(50),
    is_editable BOOLEAN DEFAULT TRUE,
    updated_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES employees(id) ON DELETE SET NULL
);
"""

CREATE_EMPLOYEE_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS employee_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_preference (employee_id, preference_key)
);
"""

CREATE_NOTIFICATION_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS notification_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    service_overdue_email BOOLEAN DEFAULT TRUE,
    service_due_soon_email BOOLEAN DEFAULT TRUE,
    fuel_expense_alert BOOLEAN DEFAULT FALSE,
    vehicle_assignment_email BOOLEAN DEFAULT TRUE,
    job_card_status_email BOOLEAN DEFAULT TRUE,
    daily_summary_email BOOLEAN DEFAULT FALSE,
    service_overdue_whatsapp BOOLEAN DEFAULT FALSE,
    service_due_soon_whatsapp BOOLEAN DEFAULT FALSE,
    fuel_expense_alert_whatsapp BOOLEAN DEFAULT FALSE,
    vehicle_assignment_whatsapp BOOLEAN DEFAULT FALSE,
    job_card_status_whatsapp BOOLEAN DEFAULT FALSE,
    daily_summary_whatsapp BOOLEAN DEFAULT FALSE,
    whatsapp_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_notification (employee_id)
);
"""

# Default system settings
DEFAULT_SYSTEM_SETTINGS = [
    ('company_name', 'Fleet Management System', 'string', 'Company name displayed across the system', 'general', True),
    ('company_email', 'admin@company.com', 'email', 'Company contact email', 'general', True),
    ('company_phone', '+1234567890', 'string', 'Company contact phone', 'general', True),
    ('fuel_price_alert_threshold', '5.00', 'number', 'Alert when fuel price per liter exceeds this amount', 'fuel', True),
    ('service_reminder_km', '10000', 'number', 'Default km for next service reminder', 'service', True),
    ('service_overdue_alert_days', '7', 'number', 'Days before service due to send alert', 'service', True),
    ('service_overdue_km', '1000', 'number', 'Km before service due to send alert', 'service', True),
    ('currency_symbol', '$', 'string', 'Currency symbol for display', 'general', True),
    ('date_format', '%Y-%m-%d', 'string', 'Date format for display', 'general', True),
    ('records_per_page', '20', 'number', 'Number of records per page in lists', 'general', True),
    ('enable_email_notifications', 'false', 'boolean', 'Enable/disable email notifications', 'notifications', True),
    ('smtp_host', 'smtp.gmail.com', 'string', 'SMTP server host', 'email', True),
    ('smtp_port', '587', 'number', 'SMTP server port', 'email', True),
    ('smtp_username', '', 'string', 'SMTP username', 'email', True),
    ('smtp_password', '', 'password', 'SMTP password', 'email', True),
    ('backup_enabled', 'true', 'boolean', 'Enable automatic database backups', 'system', True),
    ('backup_frequency', 'daily', 'string', 'Backup frequency: daily, weekly, monthly', 'system', True),
    ('whatsapp_api_enabled', 'false', 'boolean', 'Enable WhatsApp notifications', 'whatsapp', True),
    ('twilio_account_sid', '', 'string', 'Twilio Account SID', 'whatsapp', True),
    ('twilio_auth_token', '', 'password', 'Twilio Auth Token', 'whatsapp', True),
    ('twilio_whatsapp_from', '', 'string', 'Twilio WhatsApp sender (e.g., whatsapp:+14155238886)', 'whatsapp', True),
]

def init_settings_db(cursor, conn):
    """Initialize settings tables and default data"""
    cursor.execute(CREATE_SYSTEM_SETTINGS_TABLE)
    cursor.execute(CREATE_EMPLOYEE_PREFERENCES_TABLE)
    cursor.execute(CREATE_NOTIFICATION_SETTINGS_TABLE)
    
    # Insert default settings if not exist
    for setting in DEFAULT_SYSTEM_SETTINGS:
        cursor.execute("""
            INSERT INTO system_settings 
            (setting_key, setting_value, setting_type, description, category, is_editable)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE setting_key=setting_key
        """, setting)
    
    conn.commit()
