# Analytics Dashboard Data Population - Fixed

## Problem Summary
The Analytics Dashboard was not displaying any data (showing 0 for all metrics like total vehicles, fuel costs, etc.)

## Root Cause Analysis

### 1. **Status Value Mismatches**
- **Database**: Uses lowercase status values: `'available'`, `'in_use'`, `'maintenance'`, `'active'`, `'inactive'`
- **Analytics Queries**: Were checking for title case: `'In Use'`, `'Available'`, `'Under Maintenance'`, `'Inactive'`
- **Impact**: All vehicle counts and assignment counts returned 0

### 2. **Column Name Mismatches**
- **Database**: Uses `vehicle_number` field
- **Analytics Queries**: Were checking for `registration_number`
- **Impact**: Chart labels and vehicle identification failed

### 3. **Date Field Mismatches**
- **fuel_records table**: Has `fuel_date` field
- **Analytics Queries**: Were using `fueling_date`, `created_at`
- **Impact**: Fuel statistics and trends returned empty results

- **service_maintenance table**: Has `service_date` field (with `next_service_date` for future)
- **Analytics Queries**: Were using `scheduled_date`, `completion_date`, `created_at`
- **Impact**: Maintenance statistics showed incorrect data

## Fixes Applied

### File: `routes_analytics.py`

#### 1. Fixed Dashboard Stats (`/api/dashboard-stats`)
```python
# BEFORE
SUM(CASE WHEN status = 'In Use' THEN 1 ELSE 0 END) as in_use
WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
WHERE status = 'assigned'

# AFTER
SUM(CASE WHEN status = 'in_use' THEN 1 ELSE 0 END) as in_use
WHERE DATE(fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)  
WHERE status = 'active'
```

#### 2. Fixed Fuel Costs Chart (`/api/fuel-costs-chart`)
```python
# BEFORE
v.registration_number
DATE_FORMAT(fr.fueling_date, '%%Y-%%m')
WHERE DATE(fr.fueling_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)

# AFTER
v.vehicle_number
DATE_FORMAT(fr.fuel_date, '%%Y-%%m')
WHERE DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
```

#### 3. Fixed Vehicle Utilization (`/api/vehicle-utilization`)
```python
# BEFORE
v.registration_number

# AFTER
v.vehicle_number
```

#### 4. Fixed Maintenance Schedule (`/api/maintenance-schedule`)
```python
# BEFORE
sm.scheduled_date
WHERE sm.scheduled_date >= CURDATE()
ORDER BY sm.scheduled_date ASC

# AFTER
sm.next_service_date as scheduled_date
WHERE sm.next_service_date >= CURDATE()
ORDER BY sm.next_service_date ASC
```

#### 5. Fixed Fuel Efficiency Trends (`/api/fuel-efficiency-trends`)
```python
# BEFORE
v.registration_number
DATE_FORMAT(fr.fueling_date, '%%Y-%%m')
LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fueling_date)
WHERE DATE(fr.fueling_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)

# AFTER
v.vehicle_number
DATE_FORMAT(fr.fuel_date, '%%Y-%%m')
LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fuel_date)
WHERE DATE(fr.fuel_date) >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
```

#### 6. Fixed Custom Reports (`/api/generate-custom-report`)

**Fuel Analysis Report:**
```python
# BEFORE
fr.fueling_date, v.registration_number, fr.location
WHERE DATE(fr.fueling_date) BETWEEN %s AND %s
ORDER BY fr.fueling_date DESC

# AFTER
fr.fuel_date, v.vehicle_number, fr.station_name as location
WHERE DATE(fr.fuel_date) BETWEEN %s AND %s
ORDER BY fr.fuel_date DESC
```

**Maintenance Costs Report:**
```python
# BEFORE
sm.scheduled_date, sm.completion_date, v.registration_number
WHERE DATE(sm.scheduled_date) BETWEEN %s AND %s
ORDER BY sm.scheduled_date DESC

# AFTER
sm.service_date as scheduled_date, sm.service_date as completion_date, v.vehicle_number
WHERE DATE(sm.service_date) BETWEEN %s AND %s
ORDER BY sm.service_date DESC
```

**Vehicle Assignments Report:**
```python
# BEFORE
v.registration_number

# AFTER
v.vehicle_number
```

#### 7. Fixed KPI Calculations (`/api/calculate-kpis`)

**Cost per KM:**
```python
# BEFORE
DATE(sm.scheduled_date)
DATE(fr.fueling_date)

# AFTER
DATE(sm.service_date)
DATE(fr.fuel_date)
```

**Fuel Efficiency:**
```python
# BEFORE
LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fueling_date)
DATE(fr.fueling_date)

# AFTER
LAG(fr.odometer_reading) OVER (PARTITION BY fr.vehicle_id ORDER BY fr.fuel_date)
DATE(fr.fuel_date)
```

**Utilization Rate:**
```python
# BEFORE
WHERE status != 'Inactive'

# AFTER
WHERE status != 'inactive'
```

## Database Schema Reference

### Correct Field Names to Use:

**vehicles table:**
- `vehicle_number` (not `registration_number`)
- `status` values: `'available'`, `'in_use'`, `'maintenance'`, `'out_of_service'`

**fuel_records table:**
- `fuel_date` (not `fueling_date` or `created_at`)
- `station_name` (not `location`)

**service_maintenance table:**
- `service_date` (actual service date)
- `next_service_date` (future scheduled date)
- `next_service_mileage` (future scheduled mileage)
- NO `scheduled_date` or `completion_date` fields

**vehicle_assignments table:**
- `status` values: `'active'`, `'completed'`
- `assignment_date` (TIMESTAMP)
- `return_date` (TIMESTAMP, nullable)

## Verification Steps

### 1. Test Dashboard Stats
```
Visit: http://localhost:5000/analytics/dashboard
Expected: All 4 stat cards show real numbers, not 0
```

### 2. Test Fuel Costs Chart
```
Expected: Line chart displays fuel cost trends by vehicle over 6 months
```

### 3. Test Vehicle Utilization
```
Expected: Bar chart shows utilization rate % and assignment counts per vehicle
```

### 4. Test Maintenance Schedule
```
Expected: Table lists next 20 upcoming services based on next_service_date
```

### 5. Test KPIs Page
```
Visit: http://localhost:5000/analytics/kpis
Expected: All 4 KPIs calculate and display with progress bars
```

### 6. Test Report Builder
```
Visit: http://localhost:5000/analytics/report-builder
Steps:
1. Select report type (Fuel Analysis)
2. Choose date range
3. Select vehicles/employees from dropdowns (now populated via /api/vehicles and /api/employees)
4. Generate Report
5. Verify data displays in table
6. Test Excel export
7. Test PDF export
```

## Application Restart

After applying fixes, restart Flask:
```powershell
# Stop existing process
Get-Process | Where-Object {$_.ProcessName -eq 'python'} | Stop-Process -Force

# Start application
.\system\Scripts\Activate.ps1
python app.py
```

## Success Indicators

✓ Dashboard loads without 500 errors
✓ Total Vehicles shows correct count (e.g., "121 Total")
✓ Fuel Cost (30 days) shows sum of recent fuel costs
✓ Active Assignments shows count of status='active' records
✓ Maintenance Cost shows 90-day total
✓ All charts render with data
✓ KPIs page calculates all 4 metrics
✓ Report builder filters load vehicle and employee lists
✓ Custom reports generate data tables
✓ Excel/PDF exports work without errors

## Performance Notes

- All queries use proper indexes (vehicle_id, employee_id, dates)
- DATE() function usage may impact performance on large datasets
- Consider adding composite indexes if needed:
  ```sql
  CREATE INDEX idx_fuel_date_vehicle ON fuel_records(fuel_date, vehicle_id);
  CREATE INDEX idx_service_date_vehicle ON service_maintenance(service_date, vehicle_id);
  CREATE INDEX idx_assignment_date_vehicle ON vehicle_assignments(assignment_date, vehicle_id);
  ```

## Lessons Learned

1. **Always verify actual database schema** before writing queries
2. **Use consistent naming conventions** across application (lowercase vs title case)
3. **Check SQL logs** during development to catch field mismatches early
4. **Test with real data** from the start, not mock data
5. **Document field names** in database schema for reference

## Related Files Modified

- `routes_analytics.py` - All 15+ SQL queries updated
- No changes needed to:
  - `models_analytics.py` - Schema was correct
  - `templates/*.html` - Frontend was correct
  - `app.py` - Blueprint registration was correct

## Current Status

🟢 **RESOLVED** - Analytics dashboard now populates with actual data from tenant database

Last tested: November 25, 2025
Tenant tested: fleet_twt (121 vehicles migrated)
All API endpoints: ✓ Working
All dashboard components: ✓ Loading data
All export functions: ✓ Ready to use
