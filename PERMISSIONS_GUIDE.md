# Roles & Permissions System - Quick Reference

## Overview
The Roles & Permissions system provides fine-grained access control to manage what each user can do in the application.

## Database Tables

### 1. `permissions`
Stores all available permissions in the system.
- `id` - Unique identifier
- `permission_key` - Unique key (e.g., 'view_vehicles')
- `permission_name` - Display name
- `description` - What the permission allows
- `module` - Grouping category

### 2. `roles`
Stores all roles (both system and custom).
- `id` - Unique identifier
- `role_key` - Unique key (e.g., 'admin', 'manager')
- `role_name` - Display name
- `description` - Role purpose
- `is_system_role` - True for built-in roles

### 3. `role_permissions`
Links roles to their permissions (many-to-many).
- `role_id` - References roles table
- `permission_id` - References permissions table

## Default Roles

### Employee (6 permissions)
Basic user with limited access:
- View vehicles
- View own assignments
- View own fuel records
- Add fuel records
- Create service requisitions
- View requisitions

### Manager (13 permissions)
Line manager with review capabilities:
- All Employee permissions, plus:
- View all assignments
- Create assignments
- Return vehicles
- View all fuel records
- View service records and notifications
- View job cards
- Review service requisitions
- View reports

### Director (21 permissions)
Senior management with approval authority:
- All Manager permissions, plus:
- Add and edit vehicles
- Edit assignments
- Add service records
- Create job cards
- Approve service requisitions
- Export reports
- View settings

### Administrator (All 39 permissions)
Full system access including:
- All Director permissions, plus:
- Delete any records
- Manage employees
- Manage roles and permissions
- Edit system settings
- Manage backups
- Edit notification settings

## Permission Modules

### Vehicles (4 permissions)
- view_vehicles
- add_vehicle
- edit_vehicle
- delete_vehicle

### Assignments (5 permissions)
- view_assignments
- create_assignment
- edit_assignment
- return_vehicle
- view_own_assignments

### Fuel (5 permissions)
- view_all_fuel_records
- add_fuel_record
- edit_fuel_record
- delete_fuel_record
- view_own_fuel_records

### Service (5 permissions)
- view_service_records
- add_service_record
- edit_service_record
- delete_service_record
- view_service_notifications

### Job Cards (4 permissions)
- view_job_cards
- create_job_card
- edit_job_card
- delete_job_card

### Requisitions (4 permissions)
- view_requisitions
- create_requisition
- review_requisition (Line Manager)
- approve_requisition (Director)

### Employees (5 permissions)
- view_employees
- add_employee
- edit_employee
- delete_employee
- manage_roles

### Settings (6 permissions)
- view_settings
- edit_settings
- manage_backups
- view_notifications_settings
- edit_notifications_settings

### Reports (2 permissions)
- view_reports
- export_reports

## Management Interface

### Access Roles Management
1. Log in as admin
2. Go to **Settings → Roles & Permissions**

### Edit Role Permissions
1. Click **Edit** next to any role
2. Check/uncheck permissions by module
3. Use "Select All" or "Deselect All" for quick changes
4. Click **Update Permissions**

### Create Custom Role
1. Click **Create Custom Role**
2. Enter role key (e.g., 'technician')
3. Enter role name (e.g., 'Technician')
4. Add description
5. Select permissions needed
6. Click **Create Role**

### Assign Role to Employee
1. Go to **Settings → Manage Employees**
2. Click **Edit** next to employee
3. Select role from dropdown
4. Click **Update Employee**

## Using Permissions in Code

### Import Helper Module
```python
from permissions_helper import (
    has_permission,
    permission_required,
    any_permission_required
)
```

### Check Permission in Route
```python
@app.route('/some-route')
@permission_required('add_vehicle')
def some_function():
    # Only users with 'add_vehicle' permission can access
    pass
```

### Check Multiple Permissions
```python
@app.route('/some-route')
@any_permission_required(['edit_vehicle', 'delete_vehicle'])
def some_function():
    # Users need either edit OR delete permission
    pass
```

### Check Permission Programmatically
```python
if has_permission(session['employee_id'], 'delete_vehicle'):
    # Show delete button
    pass
```

## Best Practices

1. **System Roles**: Modify permissions but don't delete
2. **Custom Roles**: Create for specific job functions
3. **Least Privilege**: Grant minimum permissions needed
4. **Regular Review**: Audit role assignments quarterly
5. **Document Changes**: Note why permissions were modified

## Common Tasks

### Make Someone an Admin
```bash
python set_admin.py
```

### Reset Permissions to Default
```bash
python init_permissions.py
```

### View User's Permissions
```python
from permissions_helper import get_user_permissions
perms = get_user_permissions(user_id)
print(perms)
```

### Create Role for Fleet Supervisor
1. Create custom role: 'fleet_supervisor'
2. Select permissions:
   - All Vehicle permissions
   - All Assignment permissions
   - View fuel records
   - View service records
   - View reports

### Create Role for Mechanic
1. Create custom role: 'mechanic'
2. Select permissions:
   - View vehicles
   - View service records
   - Add service records
   - View/create/edit job cards
   - View requisitions

## Troubleshooting

### User Can't Access Page
1. Check their role assignment
2. Verify role has required permission
3. Check if account status is "active"

### Permission Not Working
1. Ensure permission exists in database
2. Check role_permissions mapping
3. Verify decorator is applied to route

### Can't Delete Role
- Roles with assigned employees cannot be deleted
- System roles cannot be deleted (only edited)
- Reassign employees first, then delete

## Security Notes

- Admin role has unrestricted access
- Inactive users cannot log in regardless of permissions
- Permission checks happen server-side (cannot be bypassed)
- All permission changes are logged with timestamps
