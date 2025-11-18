# Flask Authentication App

A complete Flask web application with user and employee authentication system using MySQL database.

## Features

- 👥 **Dual User System**: Separate authentication for Users and Employees
- 🔒 **Secure Authentication**: Password hashing with Werkzeug
- 📊 **MySQL Database**: Raw MySQL queries with PyMySQL
- 🎨 **Bootstrap UI**: Modern, responsive design
- ✅ **Form Validation**: Client and server-side validation
- 🚪 **Session Management**: Secure login/logout functionality

## Prerequisites

- Python 3.8+
- MySQL Server installed and running
- Virtual environment (already set up)

## Installation

### 1. Install Required Packages

```powershell
pip install -r requirements.txt
```

### 2. Set Up MySQL Database

Create a new MySQL database:

```sql
CREATE DATABASE flask_auth_db;
```

### 3. Configure Database Connection

Edit `app.py` and update the MySQL credentials in the `get_db_connection()` function:

```python
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',           # Your MySQL username
        password='password',    # Your MySQL password
        database='flask_auth_db',
        cursorclass=pymysql.cursors.DictCursor
    )
```

### 4. Initialize Database Tables

Run the database initialization script:

```powershell
python models.py
```

Or manually create tables using MySQL:

```sql
USE flask_auth_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running the Application

```powershell
python app.py
```

The application will start on `http://127.0.0.1:5000/`

## Application Structure

```
system/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── models.py              # Database models (User, Employee)
├── routes.py              # Application routes and views
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── user_login.html   # User login page
│   ├── user_signup.html  # User signup page
│   ├── user_dashboard.html      # User dashboard
│   ├── employee_login.html      # Employee login page
│   ├── employee_signup.html     # Employee signup page
│   └── employee_dashboard.html  # Employee dashboard
```

## Available Routes

### General
- `/` - Home page

### User Routes
- `/user/signup` - User registration
- `/user/login` - User login
- `/user/dashboard` - User dashboard (protected)

### Employee Routes
- `/employee/signup` - Employee registration
- `/employee/login` - Employee login
- `/employee/dashboard` - Employee dashboard (protected)

### Authentication
- `/logout` - Logout (both users and employees)

## Database Models

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Employee Model
- `id`: Primary key
- `employee_id`: Unique employee identifier
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `department`: Employee department
- `position`: Employee position
- `created_at`: Account creation timestamp

## Security Features

- ✅ Password hashing using Werkzeug
- ✅ Session-based authentication
- ✅ Protected routes with login_required decorator
- ✅ CSRF protection (Flask built-in)
- ✅ SQL injection prevention (Parameterized queries)

## Configuration

### Development
- Debug mode: Enabled
- Secret key: Change in production

### Production
Before deploying to production:
1. Change `SECRET_KEY` in `app.py`
2. Set `DEBUG = False`
3. Use environment variables for sensitive data
4. Configure proper MySQL user with limited privileges

## Troubleshooting

### MySQL Connection Error
- Ensure MySQL server is running
- Verify database credentials in `app.py` `get_db_connection()` function
- Check if the database `flask_auth_db` exists

### Module Not Found
```powershell
pip install -r requirements.txt
```

### Database Table Errors
```powershell
python models.py
```

## Future Enhancements

- Password reset functionality
- Email verification
- Profile picture upload
- Admin panel
- Role-based permissions
- Activity logging
- API endpoints

## License

This project is open source and available for educational purposes.
