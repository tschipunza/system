"""
Analytics and Reporting Database Models
"""

# Scheduled Reports Table
CREATE_SCHEDULED_REPORTS_TABLE = '''
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    report_type ENUM('fleet_summary', 'fuel_analysis', 'maintenance_costs', 'utilization', 'custom') NOT NULL,
    frequency ENUM('daily', 'weekly', 'monthly') NOT NULL,
    recipients TEXT NOT NULL COMMENT 'Comma-separated email addresses',
    filters JSON COMMENT 'Report filter parameters',
    last_run DATETIME,
    next_run DATETIME,
    status ENUM('active', 'paused', 'error') DEFAULT 'active',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE SET NULL
)
'''

# Report Templates Table
CREATE_REPORT_TEMPLATES_TABLE = '''
CREATE TABLE IF NOT EXISTS report_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(200) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL,
    sql_query TEXT COMMENT 'Dynamic SQL query for custom reports',
    parameters JSON COMMENT 'Report parameters and their types',
    columns JSON COMMENT 'Column definitions for display',
    created_by INT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE SET NULL
)
'''

# KPI Snapshots Table (for tracking trends over time)
CREATE_KPI_SNAPSHOTS_TABLE = '''
CREATE TABLE IF NOT EXISTS kpi_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    total_vehicles INT DEFAULT 0,
    active_vehicles INT DEFAULT 0,
    total_fuel_cost DECIMAL(12,2) DEFAULT 0,
    total_fuel_liters DECIMAL(10,2) DEFAULT 0,
    avg_fuel_efficiency DECIMAL(6,2) DEFAULT 0 COMMENT 'km per liter',
    total_maintenance_cost DECIMAL(12,2) DEFAULT 0,
    total_assignments INT DEFAULT 0,
    vehicle_utilization_rate DECIMAL(5,2) DEFAULT 0 COMMENT 'Percentage',
    avg_cost_per_km DECIMAL(8,2) DEFAULT 0,
    vehicles_needing_service INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_snapshot (snapshot_date)
)
'''

# Report Execution Log
CREATE_REPORT_LOG_TABLE = '''
CREATE TABLE IF NOT EXISTS report_execution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheduled_report_id INT,
    execution_date DATETIME NOT NULL,
    status ENUM('success', 'failed', 'pending') NOT NULL,
    records_processed INT DEFAULT 0,
    error_message TEXT,
    file_path VARCHAR(500),
    execution_time_seconds DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scheduled_report_id) REFERENCES scheduled_reports(id) ON DELETE CASCADE
)
'''

# Custom Dashboard Widgets (user customization)
CREATE_DASHBOARD_WIDGETS_TABLE = '''
CREATE TABLE IF NOT EXISTS dashboard_widgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    widget_type VARCHAR(50) NOT NULL COMMENT 'chart type: line, bar, pie, stat',
    widget_name VARCHAR(200) NOT NULL,
    data_source VARCHAR(100) NOT NULL COMMENT 'fuel_costs, maintenance, utilization, etc',
    position INT DEFAULT 0,
    size ENUM('small', 'medium', 'large') DEFAULT 'medium',
    configuration JSON COMMENT 'Widget-specific settings',
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
)
'''
