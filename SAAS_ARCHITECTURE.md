# Fleet Manager - Multi-Tenant SaaS Architecture

## Overview

Fleet Manager has been transformed into a multi-tenant SaaS application, allowing multiple companies to use the system with complete data isolation. Each company gets its own dedicated MySQL database, ensuring security and scalability.

## Architecture

### Database Isolation Strategy

**Separate Database Per Tenant**
- Each company gets a dedicated MySQL database (e.g., `fleet_acme`, `fleet_demo`)
- Complete data isolation - no shared tables
- Better performance and security
- Easy to backup/restore individual tenants
- Scalable across multiple database servers

### Main Components

1. **Main Database** (`fleet_saas_main`)
   - `companies` - Tenant/company information
   - `tenant_users` - User-to-tenant mapping (supports multi-tenancy per user)

2. **Tenant Databases** (`fleet_<subdomain>`)
   - Complete copy of all application tables (vehicles, employees, fuel_records, etc.)
   - Isolated data for each company
   - Standard schema for all tenants

## Setup Instructions

### 1. Initialize Main Database

Run the initialization script to create the main SaaS database:

```bash
python init_saas_database.py
```

This creates:
- Main database: `fleet_saas_main`
- Tables: `companies`, `tenant_users`

### 2. Configure Environment

The application automatically runs in multi-tenant mode. To disable:

```bash
# Set environment variable
set MULTI_TENANT_ENABLED=false
```

### 3. Configure Subdomain Routing

For local development, add entries to your hosts file:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
127.0.0.1  fleetmanager.local
127.0.0.1  acme.fleetmanager.local
127.0.0.1  demo.fleetmanager.local
127.0.0.1  company1.fleetmanager.local
```

### 4. Start the Application

```bash
python app.py
```

Access:
- Main site: `http://fleetmanager.local:5000`
- Company signup: `http://fleetmanager.local:5000/tenant/signup`
- Tenant portals: `http://<subdomain>.fleetmanager.local:5000`

## Company Registration Flow

### New Company Signup

1. Visit `/tenant/signup`
2. Fill in company information:
   - Company name
   - Subdomain (e.g., "acme" → acme.fleetmanager.local)
   - Contact email and phone
3. Create administrator account:
   - Username
   - Email
   - Password
4. System automatically:
   - Creates company record in main database
   - Provisions new tenant database
   - Initializes complete schema
   - Creates administrator employee account
   - Links user to tenant
   - Sets 30-day trial period

### Tenant Provisioning

When a new company signs up:

```python
1. Create company record → fleet_saas_main.companies
2. Generate database name → fleet_<subdomain>
3. Create MySQL database → CREATE DATABASE fleet_<subdomain>
4. Initialize schema → All tables (vehicles, employees, etc.)
5. Create admin user → In tenant database
6. Map user to tenant → fleet_saas_main.tenant_users
```

## Multi-Tenancy Features

### Subdomain-Based Access

- Each company has unique subdomain: `acme.fleetmanager.local`
- Automatic tenant identification from URL
- Optional custom domain support: `fleet.acme.com`

### Subscription Plans

Built-in support for different plans:

```python
- Trial (30 days, 10 vehicles, 5 users)
- Basic
- Professional
- Enterprise
```

### Tenant Limits

Plans include configurable limits:
- `max_users` - Maximum employees/users
- `max_vehicles` - Maximum fleet size
- Can be checked with: `Company.check_limits(cursor, company_id)`

### Multi-Company Access

Users can belong to multiple companies:
- Separate accounts per tenant
- Tenant selection page if user has multiple
- Switch between companies: `/tenant/switch/<company_id>`

## Technical Implementation

### Tenant Identification Middleware

```python
from tenant_middleware import TenantMiddleware

# Automatically identifies tenant from:
# 1. Subdomain (acme.fleetmanager.local)
# 2. Custom domain (fleet.acme.com)
# 3. Session fallback (for localhost)

TenantMiddleware(app)
```

### Database Context

```python
from flask import g
from tenant_manager import TenantDatabaseManager

# Tenant info available in Flask g object
g.tenant_id          # Company ID
g.tenant_db          # Database name
g.tenant_name        # Company name
g.tenant_subdomain   # Subdomain
g.tenant_plan        # Subscription plan
g.tenant_status      # active/trial/suspended

# Get database connection
def get_db_connection():
    return TenantDatabaseManager.get_tenant_connection(g.tenant_db)
```

### Decorators

```python
from tenant_middleware import require_tenant, check_tenant_limits

# Ensure tenant context exists
@require_tenant
def my_route():
    pass

# Check vehicle limit before adding
@check_tenant_limits('vehicles')
def add_vehicle():
    pass
```

## Database Schema

### Main Database (`fleet_saas_main`)

**companies**
```sql
- id
- name
- subdomain (unique)
- custom_domain (unique, nullable)
- database_name (unique)
- email, phone, address
- plan (trial/basic/professional/enterprise)
- status (trial/active/suspended/expired)
- max_users, max_vehicles
- trial_ends_at, subscription_ends_at
- company_logo, primary_color
- settings (JSON)
- created_at, updated_at
```

**tenant_users**
```sql
- id
- company_id (FK to companies)
- user_id (ID in tenant database)
- user_type (user/employee)
- role
- is_owner (boolean)
- is_active (boolean)
- created_at
```

### Tenant Databases (`fleet_<subdomain>`)

Each tenant gets complete schema:
- employees
- users
- roles
- vehicles
- assignments
- fuel_records
- services
- job_cards
- service_requisitions
- system_settings
- tenant_settings

## API Endpoints

### Tenant Management

```
GET  /tenant/signup              Company registration form
POST /tenant/signup              Create new company
POST /tenant/check-subdomain     Check subdomain availability (AJAX)
GET  /tenant/select              Tenant selection (multi-company users)
GET  /tenant/switch/<id>         Switch to different company
```

### Existing Routes

All existing routes work with tenant context:
- `/employee/login` - Login to current tenant
- `/employee/dashboard` - Tenant-specific dashboard
- `/vehicles/list` - Tenant's vehicles only
- etc.

## Security Features

### Data Isolation

- Complete database separation per tenant
- No cross-tenant data access possible
- Query isolation at database level

### Access Control

- User-tenant mapping verification
- Role-based permissions within tenant
- Owner privileges for company admins

### Subscription Management

- Trial period expiration checks
- Automatic account suspension
- Subscription renewal handling

## Scaling Considerations

### Horizontal Scaling

- Multiple app servers can share database servers
- Tenant databases can be distributed across servers
- Update `TenantDatabaseManager.TENANT_DB_BASE_CONFIG` per tenant

### Vertical Scaling

- Each tenant database can be optimized independently
- Archive old tenants to cold storage
- Resource allocation per subscription tier

### Performance

- Connection pooling per tenant
- Tenant-specific query optimization
- Independent backup schedules

## Migration from Single-Tenant

To migrate existing data:

1. Create company in main database:
```python
with TenantDatabaseManager.main_db() as conn:
    with conn.cursor() as cursor:
        company_id = Company.create(cursor, 'Legacy Company', 'legacy', 'admin@company.com')
```

2. Create tenant database:
```python
company = Company.get_by_id(cursor, company_id)
TenantDatabaseManager.create_tenant_database(company['database_name'])
```

3. Migrate data:
```bash
# Export from old database
mysqldump flask_auth_db > legacy_data.sql

# Import to tenant database
mysql fleet_legacy < legacy_data.sql
```

4. Link users to tenant:
```python
# For each employee
TenantUser.add_user_to_tenant(cursor, company_id, employee_id, 'employee')
```

## Production Deployment

### DNS Configuration

Point wildcard subdomain to your server:

```
A     fleetmanager.com           → 1.2.3.4
A     *.fleetmanager.com         → 1.2.3.4
CNAME www.fleetmanager.com       → fleetmanager.com
```

### Web Server Configuration

**Nginx Example:**

```nginx
server {
    listen 80;
    server_name fleetmanager.com *.fleetmanager.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables

```bash
export MULTI_TENANT_ENABLED=true
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_PASSWORD=your-db-password
```

### Database Backup

Backup strategy:
- Daily backup of main database (tenant metadata)
- Individual tenant backups per subscription tier
- Point-in-time recovery for active tenants

```bash
# Backup main database
mysqldump fleet_saas_main > backups/main_$(date +%Y%m%d).sql

# Backup all tenant databases
for db in $(mysql -e "SHOW DATABASES LIKE 'fleet_%';" | grep fleet_); do
    mysqldump $db > backups/${db}_$(date +%Y%m%d).sql
done
```

## Monitoring

### Key Metrics

- Active tenants count
- Trial vs paid subscriptions
- Database size per tenant
- Request rate per tenant
- Average response time
- Failed login attempts per tenant

### Health Checks

```python
@app.route('/health')
def health_check():
    # Check main database
    # Check sample tenant database
    # Check disk space
    return {'status': 'healthy'}
```

## Support & Maintenance

### Admin Operations

Common admin tasks:

1. **Suspend Company:**
```python
Company.update_status(cursor, company_id, Company.STATUS_SUSPENDED)
```

2. **Extend Trial:**
```python
from datetime import datetime, timedelta
new_date = datetime.now() + timedelta(days=30)
cursor.execute('UPDATE companies SET trial_ends_at = %s WHERE id = %s', (new_date, company_id))
```

3. **Upgrade Plan:**
```python
Company.update_subscription(cursor, company_id, 'professional', subscription_end_date)
```

## Future Enhancements

Potential additions:
- [ ] Super admin dashboard
- [ ] Tenant analytics dashboard
- [ ] Automated billing integration
- [ ] Custom branding per tenant
- [ ] White-label support
- [ ] API rate limiting per tenant
- [ ] Tenant-specific feature flags
- [ ] Multi-region support
- [ ] Tenant cloning/templates
- [ ] Data export/import tools

## Troubleshooting

### Tenant Not Found

Check:
1. Company exists in `fleet_saas_main.companies`
2. Status is 'active' or 'trial'
3. Subdomain matches URL
4. Hosts file configured (development)

### Database Connection Issues

Check:
1. Tenant database exists
2. Database name matches company record
3. MySQL user has access to tenant database
4. Connection pool not exhausted

### Session Issues

Clear session and retry:
```python
session.clear()
```

## Contact

For questions about the multi-tenant architecture:
- Review code in: `tenant_manager.py`, `tenant_middleware.py`, `models_tenant.py`
- Check initialization: `init_saas_database.py`
- Routes: `routes_tenant.py`
