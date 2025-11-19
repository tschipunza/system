# Service Requisition to Job Card/Service Record Workflow

## Overview
This document describes the complete workflow for converting approved service requisitions into either Job Cards or Service Maintenance Records with pre-populated data.

## Workflow Steps

### 1. Create Service Requisition
- **Route:** `/create-service-requisition`
- **Created by:** Employee (requester)
- **Required Information:**
  - Date requested (auto-populated)
  - Vehicle selection (reg number, make, model)
  - Current mileage
  - Work description (detailed description of required work)
  - Service history (optional notes)

### 2. Line Manager Review
- **Route:** `/view-service-requisition/<id>`
- **Action by:** Line Manager
- **Options:**
  - ✅ Approve (sends to Director for final approval)
  - ❌ Reject (workflow ends, requisition marked rejected)
- **Fields:** Comment field for approval/rejection notes

### 3. Director Approval
- **Route:** `/view-service-requisition/<id>`
- **Action by:** Director
- **Options:**
  - ✅ Approve (enables conversion to Job Card or Service Record)
  - ❌ Reject (workflow ends, requisition marked rejected)
- **Fields:** Comment field for approval/rejection notes

### 4. Convert to Job Card or Service Record
Once a requisition reaches **"Approved"** status, two buttons appear:

#### Option A: Create Job Card
- **Button:** "Create Job Card" 
- **Route:** `/create-job-card?requisition_id=<id>`
- **Pre-populated Fields:**
  - Vehicle: Auto-selected from requisition
  - Customer Name: Pre-filled from requester's username
  - Customer Email: Pre-filled from requester's email
  - Odometer In: Pre-filled from requisition current_mileage
  - Reported Issues: Pre-filled from requisition work_description
- **Additional Fields to Complete:**
  - Expected Completion Date/Time
  - Fuel Level
  - Assigned Technician
  - Priority Level
  - Diagnosis (optional)
  - Recommended Services (optional)
  - Notes (optional)

#### Option B: Add Service Record
- **Button:** "Add Service Record"
- **Route:** `/add-service?requisition_id=<id>`
- **Pre-populated Fields:**
  - Vehicle: Auto-selected from requisition
  - Odometer Reading: Pre-filled from requisition current_mileage
  - Service Description: Pre-filled from requisition work_description
  - Service History: Displayed in alert (from requisition service_history)
- **Additional Fields to Complete:**
  - Service Type (Oil Change, Tire Rotation, Brake Service, etc.)
  - Service Date
  - Cost
  - Service Provider
  - Status (Completed, Scheduled, In Progress)
  - Next Service Date (optional)
  - Next Service Mileage (optional)
  - Parts Replaced (optional)
  - Invoice/Receipt Upload (optional)
  - Notes (optional)

## Database Linkage

### Service Requisition Updates
When a Job Card or Service Record is created from an approved requisition:

- **Job Card Creation:** Updates requisition notes with "Job Card Created: JC-00001"
- **Service Record Creation:** Updates requisition notes with "Service Record Created: ID #123"

This creates a traceable link between the requisition and the resulting work order.

## Visual Indicators

### In Create Job Card Form
- Badge: "From Requisition: SR-00001" (green badge in header)
- Alert: Blue info box showing vehicle details
- Hidden field: `requisition_id` passed through form

### In Add Service Form
- Badge: "From Requisition: SR-00001" (info badge in header)
- Alert: Blue info box with vehicle details, requester info, and work description
- Service History Alert: Gray alert showing requisition service_history (if provided)
- Hidden field: `requisition_id` passed through form

## Benefits

1. **Data Consistency:** Reduces manual data entry errors
2. **Traceability:** Clear audit trail from requisition → approval → work completion
3. **Efficiency:** Pre-populated forms save time for technicians/service managers
4. **Flexibility:** Choice between Job Card (for detailed shop work) or Service Record (for completed/scheduled maintenance)
5. **Approval Workflow:** Two-tier approval ensures proper authorization before work proceeds

## Permission Requirements

- **Create Requisition:** Any authenticated employee
- **View Requisitions:** Any authenticated employee
- **Line Manager Review:** Requires "review_requisitions" permission
- **Director Approval:** Requires "approve_requisitions" permission
- **Create Job Card:** Requires "create_job_cards" permission
- **Add Service Record:** Requires "add_service" permission

## Status Tracking

Service requisitions have the following statuses:
- **Pending:** Awaiting line manager review
- **Awaiting Director Approval:** Line manager approved, awaiting director
- **Approved:** Both approvals complete, ready for conversion
- **Rejected:** Rejected at any approval stage

## Testing the Workflow

1. Log in as an employee
2. Navigate to **Service Requisitions → Create Requisition**
3. Fill in vehicle, mileage, and work description
4. Submit requisition (status: Pending)
5. Log in as line manager
6. Navigate to **Service Requisitions → View All**
7. Click on the requisition and approve (status: Awaiting Director Approval)
8. Log in as director
9. Click on the requisition and approve (status: Approved)
10. Two buttons appear: "Create Job Card" and "Add Service Record"
11. Click either button to see pre-populated form
12. Complete remaining fields and submit
13. Check requisition notes to see the link to created Job Card/Service Record

## Files Modified

### Routes (routes.py)
- `create_job_card()` - Added requisition_id parameter handling
- `add_service()` - Added requisition_id parameter handling
- Both routes fetch requisition data with JOINs to employees and vehicles tables

### Templates
- `create_job_card.html` - Added requisition badge, alert, and pre-population logic
- `add_service.html` - Added requisition badge, alert, and pre-population logic
- `view_service_requisition.html` - Added conversion buttons for approved requisitions

### Database Schema
No changes required - existing tables support this workflow.
