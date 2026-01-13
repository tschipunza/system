# Quick Start Guide - Multi-Tenant SaaS Setup

## Prerequisites
- Python 3.7+
- MySQL Server
- Windows (using PowerShell commands below)

## Setup Steps

### 1. Initialize the SaaS Database

Run the initialization script:

```powershell
cd C:\Users\itofficer\Downloads\system
.\system\Scripts\python.exe init_saas_database.py
```

Type `yes` when prompted. This creates the main database `fleet_saas_main` with tenant management tables.

### 2. Configure Hosts File (for local testing)

Edit your hosts file as Administrator:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`

Add these lines:

```
127.0.0.1  fleetmanager.local
127.0.0.1  acme.fleetmanager.local
127.0.0.1  demo.fleetmanager.local
```

Save and close.

### 3. Start the Application

```powershell
.\system\Scripts\python.exe app.py
```

The app runs in multi-tenant mode by default.

### 4. Create Your First Company

1. Open browser: `http://fleetmanager.local:5000`
2. Click **"Start Free Trial"** button
3. Fill in the form:
   - **Company Name:** Acme Corporation
   - **Subdomain:** acme
   - **Company Email:** admin@acme.com
   - **Admin Username:** admin
   - **Admin Email:** admin@acme.com
   - **Password:** password123
4. Click **"Create My Fleet Manager Account"**

### 5. Access Your Company Portal

After signup, you'll be redirected to login. Or visit directly:

`http://acme.fleetmanager.local:5000/employee/login`

Login with:
- Username: `admin`
- Password: `password123`

## What Happens Behind the Scenes?

When you create a company:

1. ✅ Company record created in `fleet_saas_main.companies`
2. ✅ New database created: `fleet_acme`
3. ✅ Complete schema initialized (vehicles, employees, fuel_records, etc.)
4. ✅ Admin employee account created in tenant database
5. ✅ User linked to tenant in `tenant_users` table
6. ✅ 30-day trial period activated

## Test Multiple Companies

Create another company with subdomain `demo`:

1. Visit: `http://fleetmanager.local:5000/tenant/signup`
2. Use subdomain: `demo`
3. Access at: `http://demo.fleetmanager.local:5000`

Each company has completely isolated data!

## Switching Between Companies

If a user belongs to multiple companies:

1. Login to any company
2. Visit `/tenant/select`
3. Choose which company to access

## Disable Multi-Tenant Mode

To use the old single-tenant mode:

```powershell
$env:MULTI_TENANT_ENABLED="false"
.\system\Scripts\python.exe app.py
```

## Common Issues

### "Company not found" Error

**Solution:** Check hosts file has the subdomain entry:
```
127.0.0.1  yoursubdomain.fleetmanager.local
```

### Database Connection Error

**Solution:** Ensure MySQL is running and credentials are correct in `tenant_manager.py`

### Can't Access Subdomain

**Solution:** Use the full URL including port:
```
http://acme.fleetmanager.local:5000
```

Not just: `http://acme.fleetmanager.local`

## Production Deployment

For production deployment:

1. Update `TenantMiddleware.MAIN_DOMAIN` in `tenant_middleware.py`
2. Configure wildcard DNS: `*.yourdomain.com → your_server_ip`
3. Set up Nginx/Apache with wildcard subdomain support
4. Use environment variables for database credentials
5. Enable SSL certificates (Let's Encrypt supports wildcards)

Example Nginx config:

```nginx
server {
    server_name yourdomain.com *.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}
```

## Key Features

### ✨ What You Get

- 🏢 **Unlimited Companies** - Each with isolated database
- 🔐 **Complete Data Isolation** - Separate MySQL database per tenant
- 🌐 **Subdomain Access** - `company.fleetmanager.local`
- 📊 **Subscription Plans** - Trial, Basic, Pro, Enterprise
- 👥 **Multi-Company Users** - Users can belong to multiple companies
- 📈 **Scalable Architecture** - Horizontal and vertical scaling
- 🎨 **Per-Company Branding** - Logo and colors
- 📦 **Easy Backup** - Individual tenant backups

### 🎯 Subscription Limits

**Trial (30 days)**
- 10 vehicles
- 5 users
- All features

**Basic**
- 25 vehicles
- 15 users

**Professional**
- 100 vehicles
- 50 users

**Enterprise**
- Unlimited vehicles
- Unlimited users
- Custom features

## Next Steps

1. ✅ Create your first company
2. ✅ Add vehicles to your fleet
3. ✅ Invite employees
4. ✅ Start tracking fuel and maintenance
5. ✅ Generate reports

## Support

For technical questions, refer to:
- `SAAS_ARCHITECTURE.md` - Complete technical documentation
- `tenant_manager.py` - Database management
- `tenant_middleware.py` - Request routing
- `models_tenant.py` - Data models

## Quick Commands Reference

```powershell
# Initialize SaaS database
.\system\Scripts\python.exe init_saas_database.py

# Start application
.\system\Scripts\python.exe app.py

# Disable multi-tenant
$env:MULTI_TENANT_ENABLED="false"

# Check MySQL databases
mysql -u root -p -e "SHOW DATABASES LIKE 'fleet_%';"

# Backup all tenant databases
Get-ChildItem "C:\Program Files\MySQL\MySQL Server 8.0\data" -Filter "fleet_*" | ForEach-Object {
    mysqldump $_.Name > "backups\$($_.Name)_$(Get-Date -Format yyyyMMdd).sql"
}
```

Enjoy your multi-tenant Fleet Manager SaaS! 🚀
