# Service Requisition System

## Overview
The Service Requisition System allows employees to submit formal requests for vehicle service and maintenance. These requests follow an approval workflow through line managers and directors before being processed.

## Features Implemented

### 1. Service Requisition Form
**Route:** `/employee/create_service_requisition`

**Form Fields:**
- **Date Requested:** Auto-populated with current date/time
- **Vehicle Selection:** Dropdown with all available vehicles
- **Vehicle Details:** Auto-populated (Registration, Make, Model)
- **Current Mileage:** Vehicle's current mileage
- **Work Description:** Detailed description of required service work (Required)
- **Service History Notes:** Any relevant historical information
- **Requested By:** Auto-populated with current user's name

### 2. Requisition List View
**Route:** `/employee/service_requisitions`

**Features:**
- View all service requisitions
- Status tracking for each approval level
- Summary cards showing counts by status:
  - Pending
  - Awaiting Director
  - Approved
  - Rejected

### 3. Requisition Detail View
**Route:** `/employee/view_service_requisition/<id>`

**Features:**
- Complete requisition details
- Vehicle information
- Requester information
- Recent service history for the vehicle
- Line manager review section
- Director approval section
- Print functionality
- Option to create job card once approved

## Approval Workflow

### Step 1: Submission
- Employee creates a service requisition
- Status: **Pending**
- Line Manager Status: **Pending**
- Director Status: **Pending**

### Step 2: Line Manager Review
- Line manager reviews the requisition
- Can approve or reject with comments
- If approved: Status changes to **Awaiting Director**
- If rejected: Status changes to **Rejected**

### Step 3: Director Approval
- Director can only approve after line manager approval
- Can approve or reject with comments
- If approved: Status changes to **Approved**
- If rejected: Status changes to **Rejected**

### Step 4: Processing
- Once approved by director, a job card can be created
- Service work can proceed

## Database Schema

### Table: `service_requisitions`

| Field | Type | Description |
|-------|------|-------------|
| id | INT (PK) | Unique identifier |
| requisition_number | VARCHAR(50) | Unique requisition number (SR-00001) |
| date_requested | TIMESTAMP | When the requisition was created |
| vehicle_id | INT (FK) | References vehicles table |
| vehicle_reg_number | VARCHAR(50) | Vehicle registration |
| vehicle_make | VARCHAR(100) | Vehicle make |
| vehicle_model | VARCHAR(100) | Vehicle model |
| current_mileage | INT | Vehicle mileage at requisition |
| work_description | TEXT | Detailed work description (Required) |
| requested_by | INT (FK) | References employees table |
| service_history | TEXT | Service history notes |
| line_manager_id | INT (FK) | Line manager who reviewed |
| line_manager_status | VARCHAR(20) | pending/approved/rejected |
| line_manager_comments | TEXT | Line manager's comments |
| line_manager_reviewed_at | TIMESTAMP | When reviewed |
| director_id | INT (FK) | Director who approved |
| director_status | VARCHAR(20) | pending/approved/rejected |
| director_comments | TEXT | Director's comments |
| director_approved_at | TIMESTAMP | When approved |
| overall_status | VARCHAR(20) | pending/awaiting_director/approved/rejected |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## Navigation

### Main Menu
- Access via sidebar: **Service & Maintenance → Service Requisitions**

### Employee Dashboard
- Quick action button: **Create Service Requisition**

## Usage Examples

### Creating a Requisition
1. Navigate to Service Requisitions from the sidebar
2. Click "Create New Requisition"
3. Select the vehicle from the dropdown
4. Vehicle details auto-populate
5. Enter current mileage (if needed)
6. Describe the work to be done
7. Add any service history notes
8. Click "Submit Requisition"

### Reviewing as Line Manager
1. View the requisition from the list
2. Review all details and service history
3. Enter comments (optional)
4. Click "Approve" or "Reject"

### Approving as Director
1. View the requisition from the list
2. Verify line manager has approved
3. Review all details
4. Enter comments (optional)
5. Click "Approve" or "Reject"

### After Approval
1. Open the approved requisition
2. Click "Create Job Card" button
3. Job card will be pre-populated with requisition details

## Status Badges

- **Pending** (Yellow/Warning): Awaiting line manager review
- **Awaiting Director** (Blue/Info): Line manager approved, awaiting director
- **Approved** (Green/Success): Fully approved by director
- **Rejected** (Red/Danger): Rejected by line manager or director

## Files Created/Modified

### New Files
1. `templates/create_service_requisition.html` - Requisition form
2. `templates/service_requisitions_list.html` - List view with status cards
3. `templates/view_service_requisition.html` - Detail view with approval sections

### Modified Files
1. `models.py` - Added CREATE_SERVICE_REQUISITIONS_TABLE schema
2. `routes.py` - Added 4 new routes for requisition management
3. `templates/base.html` - Added navigation link in sidebar
4. `templates/employee_dashboard.html` - Added quick action button

## Future Enhancements

Potential improvements:
- Email notifications for approvers
- WhatsApp notifications integration
- Bulk approval capabilities
- Export to PDF functionality
- Service cost estimation
- Historical analytics dashboard
- Mobile-responsive improvements
- Attachment uploads (photos, documents)
- Service provider recommendations
- Integration with procurement system

## Testing Checklist

- [ ] Create a service requisition
- [ ] View requisition list
- [ ] View requisition details
- [ ] Line manager approval
- [ ] Line manager rejection
- [ ] Director approval (after line manager)
- [ ] Director rejection
- [ ] Verify status badges display correctly
- [ ] Test print functionality
- [ ] Verify navigation links work
- [ ] Check service history displays
- [ ] Verify requisition number generation
