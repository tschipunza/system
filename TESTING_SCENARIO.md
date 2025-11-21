# Fleet Management System - Testing Scenario

## Test Scenario: Complete Fleet Service Workflow

This comprehensive testing scenario will help you test all major features of the Fleet Management System.

---

## Setup: Test Users & Roles

### 1. Create Test Employees
Create the following test users with different roles:

| Username | Email | Role | Department | Position |
|----------|-------|------|------------|----------|
| john.driver | john@company.com | employee | Operations | Driver |
| sarah.manager | sarah@company.com | manager | Operations | Operations Manager |
| mike.director | mike@company.com | director | Executive | Fleet Director |
| admin.user | admin@company.com | admin | IT | System Administrator |

**Password for all test accounts**: `Test@1234`

---

## Scenario: Monthly Fleet Maintenance Cycle

### Phase 1: Vehicle Setup (Admin)
**Login as**: admin.user

1. **Add Vehicles**
   - Vehicle 1: 
     - Number: `FL-001`
     - Make: `Toyota`, Model: `Hilux`, Year: `2022`
     - Type: `Pickup Truck`, Color: `White`
     - Mileage: `45,000 km`
   
   - Vehicle 2:
     - Number: `FL-002`
     - Make: `Nissan`, Model: `NP300`, Year: `2021`
     - Type: `Pickup Truck`, Color: `Silver`
     - Mileage: `62,000 km`
   
   - Vehicle 3:
     - Number: `FL-003`
     - Make: `Ford`, Model: `Ranger`, Year: `2023`
     - Type: `Pickup Truck`, Color: `Blue`
     - Mileage: `15,000 km`

2. **Verify Permissions**
   - Go to Roles & Permissions
   - Verify each role has appropriate permissions
   - Ensure `sarah.manager` has line manager permissions
   - Ensure `mike.director` has director permissions

---

### Phase 2: Vehicle Assignment (Manager)
**Login as**: sarah.manager

1. **Assign Vehicle to Driver**
   - Go to Vehicle Assignments
   - Click "Assign Vehicle"
   - Select Vehicle: `FL-001 (Toyota Hilux)`
   - Assign to: `john.driver`
   - Purpose: `Field operations - Customer site visits`
   - Expected return: 7 days from today
   - Submit assignment

2. **Verify Assignment**
   - Check Assignments List shows active assignment
   - Note assignment ID for future reference

---

### Phase 3: Daily Operations (Driver)
**Login as**: john.driver

1. **View My Assignments**
   - Go to "My Assignments"
   - Verify FL-001 is shown as currently assigned
   - Note odometer reading at assignment

2. **Add Fuel Records**
   
   **Fuel Record 1** (Day 1):
   - Vehicle: `FL-001`
   - Date: Today
   - Odometer: `45,250 km`
   - Fuel Amount: `55 liters`
   - Cost: `$95.00`
   - Station: `Shell Station - Main Street`
   - Upload receipt (optional)
   
   **Fuel Record 2** (Day 3):
   - Odometer: `45,480 km`
   - Fuel Amount: `48 liters`
   - Cost: `$83.00`
   - Station: `BP Station - Highway`
   
   **Fuel Record 3** (Day 5):
   - Odometer: `45,720 km`
   - Fuel Amount: `52 liters`
   - Cost: `$89.00`
   - Station: `Engen Station - Downtown`

3. **Notice Service Issue**
   - During Day 5, driver notices:
     - Engine making unusual noise
     - Check engine light came on
     - Vehicle pulling to the left when braking

---

### Phase 4: Service Requisition (Driver)
**Login as**: john.driver

1. **Create Service Requisition**
   - Go to Service Requisitions
   - Click "Create Service Requisition"
   - Fill in details:
     - Vehicle: `FL-001 (Toyota Hilux)`
     - Current Mileage: `45,720 km`
     - Work Description:
       ```
       Vehicle requires urgent attention:
       1. Engine making unusual knocking noise
       2. Check engine light activated
       3. Brakes pulling to the left - safety concern
       4. Due for regular 45,000km service
       ```
     - Service History:
       ```
       Last service: 30,000km (6 months ago)
       - Oil change performed
       - Air filter replaced
       - Tire rotation completed
       No major issues reported at last service
       ```
   - Submit requisition
   - Note the requisition number (e.g., `SR-00001`)

2. **Verify Requisition**
   - Check requisition appears in list
   - Status should be "Pending"
   - Awaiting Line Manager Review

---

### Phase 5: Line Manager Review (Manager)
**Login as**: sarah.manager

1. **Review Service Requisition**
   - Go to Service Requisitions
   - Open requisition `SR-00001`
   - Review the details
   - Line Manager Action:
     - Status: `Approve`
     - Comments:
       ```
       Approved for immediate service.
       Safety concern with brakes requires priority attention.
       Authorized spend up to $1,500.
       Please also complete the 45,000km scheduled maintenance.
       ```
   - Submit review

2. **Verify Status Change**
   - Requisition status should now be "Awaiting Director Approval"
   - Notification sent to director

---

### Phase 6: Director Approval (Director)
**Login as**: mike.director

1. **Review & Approve Requisition**
   - Go to Service Requisitions
   - Open requisition `SR-00001`
   - Review line manager comments
   - Director Action:
     - Status: `Approve`
     - Comments:
       ```
       Final approval granted.
       Budget approved: $1,500
       Please use our approved service provider: ABC Auto Service
       Request detailed diagnostic report for the engine issue.
       ```
   - Submit approval

2. **Verify Final Approval**
   - Requisition status should now be "Approved"
   - Two action buttons should appear:
     - "Create Job Card"
     - "Add Service Record"

---

### Phase 7A: Convert to Job Card (Manager/Admin)
**Login as**: sarah.manager or admin.user

1. **Create Job Card from Requisition**
   - Open approved requisition `SR-00001`
   - Click "Create Job Card"
   - Form should be pre-populated:
     - Vehicle: `FL-001` (pre-selected)
     - Customer Name: `john.driver` (pre-filled)
     - Customer Email: `john@company.com` (pre-filled)
     - Odometer In: `45,720 km` (pre-filled)
     - Reported Issues: (pre-filled from requisition)
   
2. **Complete Job Card Details**
   - Expected Completion: 2 days from now, 5:00 PM
   - Fuel Level: `1/2 Tank`
   - Diagnosis:
     ```
     Diagnostic results:
     - Engine knock caused by low oil pressure
     - Faulty oil pump identified
     - Brake caliper seized on left front wheel
     - Check engine code: P0520 (Oil Pressure Sensor)
     ```
   - Recommended Services:
     ```
     1. Replace oil pump
     2. Replace oil pressure sensor
     3. Replace left front brake caliper
     4. Complete 45,000km service package
     5. Road test after repairs
     ```
   - Assigned Technician: Select available technician
   - Priority: `High`
   - Notes: `Customer waiting - provide courtesy vehicle if needed`
   - Submit job card

3. **Verify Job Card**
   - Note job card number (e.g., `JC000001`)
   - Status should be "Open"
   - View job card details to confirm all information

---

### Phase 7B: Update Job Card Progress (Technician/Manager)
**Login as**: sarah.manager

1. **Update Job Card - In Progress**
   - Go to Job Cards
   - Open job card `JC000001`
   - Click "Update Status"
   - Change to: `In Progress`
   - Add notes: `Parts ordered, work commenced`

2. **Add Labor & Parts**
   - Add Labor Entry:
     - Description: `Diagnostic and engine repair`
     - Hours: `6.5`
     - Rate: `$85/hour`
   
   - Add Parts:
     - `Oil pump assembly - $320`
     - `Oil pressure sensor - $65`
     - `Brake caliper - $180`
     - `Engine oil 5W-30 (5L) - $55`
     - `Oil filter - $25`
     - `Air filter - $30`
     - `Brake fluid - $15`

3. **Complete Job Card**
   - Update Status: `Completed`
   - Odometer Out: `45,725 km`
   - Actual Completion: Current date/time
   - Final Notes:
     ```
     All repairs completed successfully.
     Oil pump replaced, engine running smoothly.
     Brake system repaired and tested.
     45,000km service completed.
     Road test performed - all systems operational.
     Customer can collect vehicle.
     ```

---

### Phase 8: Service Record (Alternative Path)
**If you didn't create a job card, test this flow**

**Login as**: sarah.manager

1. **Add Service Record from Requisition**
   - Open approved requisition `SR-00001`
   - Click "Add Service Record"
   - Form should be pre-populated:
     - Vehicle: `FL-001` (pre-selected)
     - Odometer Reading: `45,720 km` (pre-filled)
     - Service Description: (pre-filled from work description)

2. **Complete Service Details**
   - Service Type: `Repair`
   - Service Date: Today
   - Service Provider: `ABC Auto Service`
   - Cost: `$1,285.00`
   - Next Service Date: 3 months from now
   - Next Service Mileage: `60,000 km`
   - Parts Replaced:
     ```
     - Oil pump assembly
     - Oil pressure sensor
     - Left front brake caliper
     - Oil filter
     - Air filter
     ```
   - Status: `Completed`
   - Notes: `Vehicle repaired and tested - ready for return to service`
   - Upload invoice (optional)
   - Submit record

---

### Phase 9: Vehicle Return (Driver)
**Login as**: john.driver

1. **Return Vehicle**
   - Go to "My Assignments"
   - Click "Return Vehicle" for FL-001
   - Return Details:
     - Return Date: Today
     - Odometer at Return: `45,750 km`
     - Fuel Level at Return: `Full`
     - Condition: `Good`
     - Notes: `Vehicle serviced and running well. All issues resolved.`
   - Submit return

2. **Verify Return**
   - Assignment status should change to "Returned"
   - Vehicle should be available for new assignments

---

### Phase 10: Reports & Analytics (Admin/Manager/Director)
**Login as**: admin.user or mike.director

1. **Review Fuel Efficiency**
   - Go to Fuel Records
   - Filter by Vehicle: FL-001
   - Calculate total fuel consumption during assignment
   - Check fuel efficiency trends

2. **Service History Review**
   - Go to Vehicles List
   - Click on FL-001
   - View complete service history
   - Verify requisition linkage to service record/job card

3. **Cost Analysis**
   - Review total service costs for FL-001
   - Compare against budget
   - Check fuel costs for the assignment period

4. **Service Notifications**
   - Go to Service Notifications
   - Check upcoming service requirements
   - Verify next service date/mileage calculations

---

## Additional Test Scenarios

### Scenario A: Rejected Requisition
1. Create a new requisition as driver
2. Line manager rejects with reason: "Insufficient justification"
3. Driver creates new requisition with more details
4. Full approval cycle

### Scenario B: Multiple Vehicle Management
1. Assign FL-002 to another driver
2. Create overlapping fuel records
3. Schedule preventive maintenance
4. Track multiple service records

### Scenario C: Emergency Repair
1. Driver reports breakdown
2. Create urgent requisition
3. Fast-track approval process
4. Create job card with "Critical" priority

### Scenario D: Scheduled Maintenance
1. Create requisition for routine 60,000km service
2. Normal approval flow
3. Convert to service record
4. Set next service intervals

---

## Expected Results Checklist

### ✅ Vehicle Management
- [ ] Vehicles created with all details
- [ ] Vehicle status updates correctly
- [ ] Mileage tracking accurate
- [ ] Service history visible

### ✅ Assignments
- [ ] Assignment created successfully
- [ ] Driver can view their assignments
- [ ] Return process works correctly
- [ ] Assignment history maintained

### ✅ Fuel Tracking
- [ ] Fuel records created with receipts
- [ ] Odometer readings increase logically
- [ ] Cost calculations correct
- [ ] Filtering and search work

### ✅ Service Requisitions
- [ ] Requisition creation form works
- [ ] Auto-generation of requisition numbers
- [ ] Approval workflow functions (Line Manager → Director)
- [ ] Status tracking accurate
- [ ] Comments saved correctly
- [ ] Email notifications sent (if configured)

### ✅ Requisition Conversion
- [ ] "Create Job Card" button appears when approved
- [ ] "Add Service Record" button appears when approved
- [ ] Pre-population of data works correctly
- [ ] Linkage between requisition and job card/service maintained

### ✅ Job Cards
- [ ] Job card creation with pre-filled data
- [ ] Auto-generation of job card numbers
- [ ] Status workflow (Open → In Progress → Completed)
- [ ] Labor and parts tracking
- [ ] Cost calculations
- [ ] Print functionality

### ✅ Service Records
- [ ] Service record creation with pre-filled data
- [ ] Next service date/mileage calculation
- [ ] File upload for invoices
- [ ] Service history linkage
- [ ] Display in vehicle service history

### ✅ Roles & Permissions
- [ ] Each role has appropriate access
- [ ] Permission restrictions enforced
- [ ] Admin can manage roles
- [ ] New permissions can be added

### ✅ Reports & Analytics
- [ ] Fuel efficiency reports
- [ ] Service cost tracking
- [ ] Service notification system
- [ ] Vehicle availability status

---

## Performance Testing

### Load Test Scenario
1. Create 20 vehicles
2. Create 10 employees
3. Generate 50 assignments (mix of active/returned)
4. Add 200 fuel records
5. Create 30 service requisitions (various stages)
6. Generate 25 job cards
7. Add 40 service records

**Test**: 
- Page load times
- Search/filter performance
- Report generation speed
- Database query efficiency

---

## Notes
- Take screenshots at each major step for documentation
- Note any bugs or issues encountered
- Record response times for key operations
- Test on different browsers (Chrome, Firefox, Edge)
- Test responsiveness on mobile/tablet devices
- Verify print layouts for requisitions and job cards

---

## Test Data Cleanup

After testing, you can:
1. Use backup/restore functionality to reset database
2. Manually delete test records in reverse order (service → job cards → requisitions → fuel → assignments → vehicles → employees)
3. Keep test data for demo purposes

---

**Happy Testing! 🚗🔧**
