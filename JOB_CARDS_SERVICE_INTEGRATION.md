# Job Cards & Service Records Integration

## Overview
The Job Cards and Service Records systems are now fully integrated. When a job card is marked as "completed", a service record is automatically created in the service history.

## How It Works

### 1. Job Card Workflow
1. **Create Job Card** (`/create-job-card`)
   - Assign vehicle, customer details, and reported issues
   - Set priority (normal/high/urgent) and technician
   - Job card gets auto-generated number (e.g., JC000001)

2. **Add Parts & Labor** (`/view-job-card/<id>`)
   - Add line items for parts used (description, quantity, unit price)
   - Add labor entries with descriptions and costs
   - Total cost is calculated automatically

3. **Complete Job Card** (`/edit-job-card/<id>`)
   - Update diagnosis and recommended services
   - Enter odometer_out reading
   - **Change status to "completed"**
   - System automatically creates service record

### 2. Automatic Service Record Creation
When a job card status changes to "completed":

**Data Transfer:**
- **Vehicle ID** → Linked to same vehicle
- **Service Type** → Auto-detected from diagnosis keywords:
  - Contains "oil change" → Oil Change
  - Contains "brake" → Brake Service
  - Contains "tire" → Tire Rotation
  - Contains "engine/tune" → Engine Tune-up
  - Contains "inspection" → Inspection
  - Contains "repair" → Repair
  - Default → General Service
- **Service Date** → Current date
- **Cost** → Total cost from job card (parts + labor)
- **Odometer Reading** → odometer_out value
- **Description** → Diagnosis or reported issues
- **Parts Replaced** → Formatted list of all parts from job card items
- **Performed By** → Assigned technician (or session user if not assigned)
- **Job Card ID** → Reference link to original job card
- **Status** → "completed"
- **Notes** → Auto-generated text: "Auto-generated from Job Card: JC000001"

**Vehicle Update:**
- Updates vehicle's `last_service_date` to current date
- Updates vehicle's `mileage` to odometer_out value

### 3. Linked Records

**From Job Card View:**
- Completed job cards show "Service Record Created" card
- Includes link to view the auto-generated service record

**From Service Record View:**
- Service records show "Related Job Card" section if auto-generated
- Includes link back to the original job card
- Note: "This service record was automatically generated from a completed job card."

**In Service Lists:**
- Service records auto-generated from job cards show:
  - 📋 "From Job Card" indicator in service type column
  - All standard service record features still available

## Database Schema

### New Fields

**service_maintenance table:**
```sql
job_card_id INT NULL
FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE SET NULL
```

### Data Flow
```
Job Card (Open) → Add Parts/Labor → Mark Completed → 
  → Auto-create Service Record → Link via job_card_id → 
  → Update Vehicle Last Service
```

## Key Features

### Prevents Duplication
- Service records are only created once per job card
- System checks if job was previously completed to avoid duplicate records

### Maintains Independence
- Job cards can exist without service records (for open/in-progress work)
- Service records can be created manually without job cards
- Both systems remain fully functional independently

### Preserves History
- Job cards maintain complete work order history
- Service records maintain complete service history
- Links between records preserved for traceability

## Use Cases

### Scenario 1: Customer Brings Vehicle for Service
1. Create job card with customer info and reported issues
2. Diagnose problems and add parts/labor as work progresses
3. Track work-in-progress with real-time cost updates
4. Mark complete when done → Service record auto-created
5. Customer can view job card details
6. Service history automatically updated for vehicle

### Scenario 2: Manual Service Record Entry
1. For services performed elsewhere or historical data
2. Create service record directly via "Add Service Record"
3. No job card required
4. Full control over all service record fields

### Scenario 3: Review Service History
1. View vehicle service history
2. See which services came from job cards (indicated by icon)
3. Click through to view original job card details
4. Complete audit trail of work performed

## Benefits

✅ **Eliminates Data Re-entry**: Service details automatically transferred from job card
✅ **Maintains Traceability**: Clear links between work orders and service history
✅ **Accurate Cost Tracking**: Total costs calculated from detailed parts/labor breakdown
✅ **Automated Workflows**: Status change triggers record creation
✅ **Flexible System**: Can use job cards, manual service records, or both
✅ **Complete History**: Full service history always available per vehicle
✅ **Customer Communication**: Professional job cards with detailed breakdown

## Technical Notes

### Routes Modified
- `edit_job_card()` - Added auto-create logic for service records
- `view_job_card()` - Added service record lookup for completed jobs
- Database init - Added job_card_id foreign key

### Templates Updated
- `view_job_card.html` - Shows service record link when completed
- `view_service.html` - Shows job card link when auto-generated
- `service_maintenance.html` - Indicator for job card-originated records
- `vehicle_service_history.html` - Indicator for job card-originated records

### Status Workflow
- **open** → New job card created
- **in_progress** → Work has started
- **on_hold** → Waiting for parts or approval
- **completed** → Work finished → **Triggers service record creation**

## Future Enhancements (Possible)
- Email notification to customer when job completed
- PDF generation of job card for customer records
- Parts inventory tracking and auto-deduction
- Labor time tracking with start/stop timers
- Customer approval workflow for additional work
- Integration with invoicing system
