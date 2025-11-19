# Database initialization script
# Run this file to create the necessary tables

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_EMPLOYEES_TABLE = """
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    role VARCHAR(50) DEFAULT 'employee',
    status VARCHAR(20) DEFAULT 'active',
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

CREATE_VEHICLES_TABLE = """
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(50) UNIQUE NOT NULL,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(50),
    vehicle_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'available',
    mileage INT,
    last_service_date DATE,
    notes TEXT,
    added_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES employees(id) ON DELETE SET NULL
);
"""

CREATE_VEHICLE_ASSIGNMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS vehicle_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    employee_id INT NOT NULL,
    assigned_by INT,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP NULL,
    status VARCHAR(20) DEFAULT 'active',
    mileage_at_assignment INT,
    mileage_at_return INT,
    purpose TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES employees(id) ON DELETE SET NULL
);
"""

CREATE_FUEL_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS fuel_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    employee_id INT NOT NULL,
    fuel_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fuel_amount DECIMAL(10, 2) NOT NULL,
    fuel_cost DECIMAL(10, 2) NOT NULL,
    odometer_reading INT,
    fuel_type VARCHAR(50),
    station_name VARCHAR(100),
    receipt_path VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
"""

CREATE_SERVICE_MAINTENANCE_TABLE = """
CREATE TABLE IF NOT EXISTS service_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    service_date DATE NOT NULL,
    service_provider VARCHAR(200),
    cost DECIMAL(10, 2),
    odometer_reading INT,
    next_service_date DATE,
    next_service_mileage INT,
    description TEXT,
    parts_replaced TEXT,
    invoice_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed',
    performed_by INT,
    job_card_id INT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE SET NULL
);
"""

CREATE_JOB_CARDS_TABLE = """
CREATE TABLE IF NOT EXISTS job_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_card_number VARCHAR(50) UNIQUE NOT NULL,
    vehicle_id INT NOT NULL,
    customer_name VARCHAR(200),
    customer_phone VARCHAR(50),
    customer_email VARCHAR(100),
    date_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_completion TIMESTAMP,
    date_out TIMESTAMP NULL,
    odometer_in INT,
    odometer_out INT,
    fuel_level VARCHAR(20),
    reported_issues TEXT,
    diagnosis TEXT,
    recommended_services TEXT,
    assigned_technician INT,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    total_cost DECIMAL(10, 2) DEFAULT 0.00,
    labor_cost DECIMAL(10, 2) DEFAULT 0.00,
    parts_cost DECIMAL(10, 2) DEFAULT 0.00,
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_technician) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE SET NULL
);
"""

CREATE_JOB_CARD_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS job_card_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_card_id INT NOT NULL,
    item_type VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(10, 2) DEFAULT 1,
    unit_price DECIMAL(10, 2) DEFAULT 0.00,
    total_price DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
);
"""

CREATE_SERVICE_REQUISITIONS_TABLE = """
CREATE TABLE IF NOT EXISTS service_requisitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requisition_number VARCHAR(50) UNIQUE NOT NULL,
    date_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vehicle_id INT NOT NULL,
    vehicle_reg_number VARCHAR(50),
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    current_mileage INT,
    work_description TEXT NOT NULL,
    requested_by INT NOT NULL,
    service_history TEXT,
    line_manager_id INT,
    line_manager_status VARCHAR(20) DEFAULT 'pending',
    line_manager_comments TEXT,
    line_manager_reviewed_at TIMESTAMP NULL,
    director_id INT,
    director_status VARCHAR(20) DEFAULT 'pending',
    director_comments TEXT,
    director_approved_at TIMESTAMP NULL,
    overall_status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (line_manager_id) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (director_id) REFERENCES employees(id) ON DELETE SET NULL
);
"""

def init_db():
    """Initialize database tables"""
    from app import get_db_connection
    from models_settings import init_settings_db
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_EMPLOYEES_TABLE)
        cursor.execute(CREATE_VEHICLES_TABLE)
        cursor.execute(CREATE_VEHICLE_ASSIGNMENTS_TABLE)
        cursor.execute(CREATE_FUEL_RECORDS_TABLE)
        cursor.execute(CREATE_SERVICE_MAINTENANCE_TABLE)
        cursor.execute(CREATE_JOB_CARDS_TABLE)
        cursor.execute(CREATE_JOB_CARD_ITEMS_TABLE)
        cursor.execute(CREATE_SERVICE_REQUISITIONS_TABLE)
        
        # Initialize settings tables and defaults
        init_settings_db(cursor, conn)
        
        conn.commit()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db()
