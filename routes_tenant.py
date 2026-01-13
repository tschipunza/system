"""
Tenant registration and onboarding routes
Handles company signup, database provisioning, and initial setup
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from tenant_manager import TenantDatabaseManager, init_main_database
from models_tenant import Company, TenantUser
import re

tenant_bp = Blueprint('tenant', __name__, url_prefix='/tenant')


@tenant_bp.route('/signup', methods=['GET', 'POST'])
def tenant_signup():
    """
    Company registration page
    Creates new tenant with isolated database
    """
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name', '').strip()
        subdomain = request.form.get('subdomain', '').strip().lower()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Admin user credentials
        admin_username = request.form.get('admin_username', '').strip()
        admin_email = request.form.get('admin_email', '').strip()
        admin_password = request.form.get('admin_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not company_name or len(company_name) < 3:
            errors.append('Company name must be at least 3 characters')
        
        if not subdomain or len(subdomain) < 3:
            errors.append('Subdomain must be at least 3 characters')
        elif not re.match(r'^[a-z0-9-]+$', subdomain):
            errors.append('Subdomain can only contain lowercase letters, numbers, and hyphens')
        elif subdomain in ['www', 'admin', 'api', 'app', 'dashboard', 'support', 'help']:
            errors.append('This subdomain is reserved')
        
        if not email or '@' not in email:
            errors.append('Valid email address is required')
        
        if not admin_username or len(admin_username) < 3:
            errors.append('Admin username must be at least 3 characters')
        
        if not admin_password or len(admin_password) < 6:
            errors.append('Admin password must be at least 6 characters')
        elif admin_password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if subdomain is available
        if not errors:
            try:
                with TenantDatabaseManager.main_db() as conn:
                    with conn.cursor() as cursor:
                        existing = Company.get_by_subdomain(cursor, subdomain)
                        if existing:
                            errors.append('This subdomain is already taken')
            except:
                errors.append('Error checking subdomain availability')
        
        # If validation fails, show errors
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('tenant_signup.html',
                                 company_name=company_name,
                                 subdomain=subdomain,
                                 email=email,
                                 phone=phone,
                                 admin_username=admin_username,
                                 admin_email=admin_email)
        
        # Create company and provision database
        try:
            with TenantDatabaseManager.main_db() as conn:
                with conn.cursor() as cursor:
                    # Create company record
                    company_id = Company.create(
                        cursor, 
                        name=company_name,
                        subdomain=subdomain,
                        email=email,
                        phone=phone,
                        plan='trial'
                    )
                    conn.commit()
                    
                    # Get company details
                    company = Company.get_by_id(cursor, company_id)
            
            # Create tenant database
            database_name = company['database_name']
            success = TenantDatabaseManager.create_tenant_database(database_name)
            
            if not success:
                raise Exception("Failed to create tenant database")
            
            # Create admin user in tenant database
            from werkzeug.security import generate_password_hash
            import random
            import string
            
            # Generate a unique employee_id
            emp_id = f"EMP{''.join(random.choices(string.digits, k=6))}"
            
            with TenantDatabaseManager.tenant_db(database_name) as conn:
                with conn.cursor() as cursor:
                    # Create admin employee account
                    cursor.execute('''
                        INSERT INTO employees (employee_id, username, email, password_hash, role, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (emp_id, admin_username, admin_email, 
                          generate_password_hash(admin_password),
                          'Administrator', 'active'))
                    
                    employee_id = cursor.lastrowid
                    conn.commit()
            
            # Link admin user to tenant
            with TenantDatabaseManager.main_db() as conn:
                with conn.cursor() as cursor:
                    TenantUser.add_user_to_tenant(
                        cursor,
                        company_id=company_id,
                        user_id=employee_id,
                        user_type='employee',
                        role='administrator',
                        is_owner=True
                    )
                    conn.commit()
            
            # Success - redirect to login with subdomain
            flash(f'🎉 Welcome to Fleet Manager! Your account has been created successfully. Trial period: 30 days.', 'success')
            flash(f'Your fleet management portal is ready at: {subdomain}.fleetmanager.local', 'info')
            
            # Set tenant in session for immediate login
            session['tenant_id'] = company_id
            session['tenant_name'] = company_name
            
            return redirect(url_for('employee_login'))
        
        except Exception as e:
            # Rollback - delete company and database if created
            try:
                with TenantDatabaseManager.main_db() as conn:
                    with conn.cursor() as cursor:
                        if 'company_id' in locals():
                            cursor.execute('DELETE FROM companies WHERE id = %s', (company_id,))
                            conn.commit()
                
                if 'database_name' in locals():
                    TenantDatabaseManager.drop_tenant_database(database_name)
            except:
                pass
            
            flash(f'Error creating company: {str(e)}', 'danger')
            return render_template('tenant_signup.html')
    
    # GET request - show signup form
    return render_template('tenant_signup.html')


@tenant_bp.route('/check-subdomain', methods=['POST'])
def check_subdomain():
    """
    AJAX endpoint to check subdomain availability
    """
    from flask import jsonify
    
    subdomain = request.json.get('subdomain', '').strip().lower()
    
    if not subdomain:
        return jsonify({'available': False, 'message': 'Subdomain is required'})
    
    if not re.match(r'^[a-z0-9-]+$', subdomain):
        return jsonify({'available': False, 'message': 'Invalid characters in subdomain'})
    
    if subdomain in ['www', 'admin', 'api', 'app', 'dashboard', 'support', 'help']:
        return jsonify({'available': False, 'message': 'This subdomain is reserved'})
    
    try:
        with TenantDatabaseManager.main_db() as conn:
            with conn.cursor() as cursor:
                existing = Company.get_by_subdomain(cursor, subdomain)
                
                if existing:
                    return jsonify({'available': False, 'message': 'Subdomain already taken'})
                else:
                    return jsonify({'available': True, 'message': 'Subdomain is available!'})
    except Exception as e:
        return jsonify({'available': False, 'message': 'Error checking availability'})


@tenant_bp.route('/select')
def tenant_select():
    """
    Tenant selection page for users who belong to multiple companies
    """
    if 'employee_id' not in session and 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session.get('employee_id') or session.get('user_id')
    user_type = 'employee' if 'employee_id' in session else 'user'
    
    try:
        with TenantDatabaseManager.main_db() as conn:
            with conn.cursor() as cursor:
                tenants = TenantUser.get_user_tenants(cursor, user_id, user_type)
        
        if len(tenants) == 1:
            # Only one tenant, auto-select
            session['tenant_id'] = tenants[0]['id']
            session['tenant_name'] = tenants[0]['name']
            return redirect(url_for('employee_dashboard' if user_type == 'employee' else 'user_dashboard'))
        
        return render_template('tenant_select.html', tenants=tenants)
    
    except Exception as e:
        flash(f'Error loading companies: {str(e)}', 'danger')
        return redirect(url_for('index'))


@tenant_bp.route('/switch/<int:company_id>')
def tenant_switch(company_id):
    """
    Switch to a different tenant/company
    """
    if 'employee_id' not in session and 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session.get('employee_id') or session.get('user_id')
    user_type = 'employee' if 'employee_id' in session else 'user'
    
    try:
        # Verify user has access to this tenant
        with TenantDatabaseManager.main_db() as conn:
            with conn.cursor() as cursor:
                if TenantUser.verify_user_access(cursor, company_id, user_id, user_type):
                    company = Company.get_by_id(cursor, company_id)
                    
                    if company and company['status'] in ['active', 'trial']:
                        session['tenant_id'] = company['id']
                        session['tenant_name'] = company['name']
                        
                        flash(f'Switched to {company["name"]}', 'success')
                        return redirect(url_for('employee_dashboard' if user_type == 'employee' else 'user_dashboard'))
                
                flash('Access denied to this company', 'danger')
                return redirect(url_for('tenant.tenant_select'))
    
    except Exception as e:
        flash(f'Error switching company: {str(e)}', 'danger')
        return redirect(url_for('index'))
