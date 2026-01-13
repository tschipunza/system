# Scheduled Reports - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email
Create `.env` file:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Fleet Management System
```

**For Gmail**: Generate App Password at https://myaccount.google.com/apppasswords

### 3. Test Email Configuration
```bash
python test_scheduled_reports.py
```

### 4. Start Application
```bash
python app.py
```

## 📧 Create Your First Report

### Via Web Interface
1. Log in as admin
2. Navigate: **Analytics → Scheduled Reports**
3. Click **"Create New Report"**
4. Fill form:
   - **Name**: "Weekly Fuel Summary"
   - **Type**: "Fuel Analysis"
   - **Frequency**: "Weekly"
   - **Format**: "Excel"
   - **Recipients**: "manager@example.com, finance@example.com"
5. Click **"Create Scheduled Report"**
6. Click **"Run Now"** to test immediately

## 📊 Report Types Available

### 1. Fuel Analysis
- Total fuel consumption
- Fuel costs by vehicle
- Cost per kilometer
- Fuel efficiency trends
- **Best for**: Fleet managers, finance team

### 2. Maintenance Costs
- Service and repair expenses
- Costs by vehicle
- Maintenance trends
- Upcoming service reminders
- **Best for**: Maintenance managers, budget planning

### 3. Vehicle Assignments
- Current assignments
- Assignment history
- Vehicle utilization
- Employee assignment tracking
- **Best for**: Operations managers, HR

## ⏰ Schedule Options

| Frequency | Runs At | Use Case |
|-----------|---------|----------|
| **Daily** | 8:00 AM every day | Real-time tracking, daily operations |
| **Weekly** | Monday 8:00 AM | Weekly reviews, team meetings |
| **Monthly** | 1st of month 8:00 AM | Monthly reports, board meetings |

## 📋 Using Filters

### Include All Data (Default)
Leave all checkboxes **unchecked** to include all vehicles and employees.

### Specific Vehicles
Check only the vehicles you want in the report.
**Example**: Only company trucks, exclude personal vehicles

### Specific Employees
Check only the employees you want to track.
**Example**: Only drivers, exclude admin staff

### Combined Filters
Check both vehicles AND employees for precise reports.
**Example**: Fuel records for specific driver on specific vehicle

## 📤 Report Formats

### Excel (XLSX)
- ✅ Best for data analysis
- ✅ Can edit and customize
- ✅ Import into other systems
- ✅ Create charts and pivot tables
- 📦 File size: Small (good for large datasets)

### PDF
- ✅ Best for presentations
- ✅ Professional appearance
- ✅ Print-ready
- ✅ Cannot be edited
- 📦 File size: Larger (good for final reports)

## 🔧 Managing Reports

### Run Immediately
Click **"Run Now"** to execute without waiting for schedule.
**Use case**: Test before schedule, urgent reports

### View History
Click **"History"** to see:
- When report last ran
- Success/failure status
- Execution duration
- Number of records
- Any error messages

### Pause Report
Click **"Disable"** to temporarily stop scheduled execution.
**Use case**: Vacation, temporary suspension

### Resume Report
Click **"Enable"** to restart scheduled execution.

### Delete Report
Click **"Delete"** to permanently remove report and stop all future executions.

## 💡 Best Practices

### Recipients
- ✅ Use comma-separated emails: `user1@example.com, user2@example.com`
- ✅ Include multiple recipients for redundancy
- ✅ Use distribution lists for teams
- ❌ Don't include invalid email addresses

### Naming
- ✅ Use descriptive names: "Weekly Fuel Report - Operations Team"
- ✅ Include frequency in name: "Daily Maintenance Summary"
- ✅ Include department: "Finance - Monthly Cost Report"
- ❌ Avoid generic names: "Report 1", "Test Report"

### Scheduling
- ✅ Start with weekly, adjust based on needs
- ✅ Schedule during off-peak hours
- ✅ Coordinate with team meeting schedules
- ❌ Don't schedule too many reports at same time

### Filters
- ✅ Use filters to reduce report size
- ✅ Create separate reports for different teams
- ✅ Filter by active vehicles only
- ❌ Don't create overly complex filter combinations

## 🐛 Troubleshooting

### Email Not Received
1. Check spam/junk folder
2. Verify email address is correct
3. Run test: `python test_scheduled_reports.py`
4. Check execution history for errors

### Report Shows No Data
1. Check date range (reports cover last period)
2. Verify filters aren't too restrictive
3. Ensure data exists in database
4. Check execution history for details

### Report Not Running on Schedule
1. Ensure Flask app is running
2. Check report is **enabled** (not disabled)
3. Verify next run date is in future
4. Check application logs

### Gmail Issues
- ✅ Use App Password (not regular password)
- ✅ Enable 2-Factor Authentication first
- ✅ Check SMTP port is 587
- ❌ Don't use "Less secure apps" setting

## 📈 Usage Examples

### Example 1: Weekly Fuel Report for Management
```
Name: Weekly Fuel Report - Management
Type: Fuel Analysis
Frequency: Weekly (Monday 8 AM)
Format: PDF (for presentations)
Recipients: manager@company.com, ceo@company.com
Filters: All vehicles, All employees
```

### Example 2: Daily Operations Report
```
Name: Daily Operations Summary
Type: Vehicle Assignments
Frequency: Daily (8 AM)
Format: Excel (for data analysis)
Recipients: operations@company.com
Filters: Active vehicles only
```

### Example 3: Monthly Financial Report
```
Name: Monthly Maintenance Costs - Finance
Type: Maintenance Costs
Frequency: Monthly (1st at 8 AM)
Format: PDF (for board meeting)
Recipients: finance@company.com, cfo@company.com
Filters: All vehicles
```

### Example 4: Driver-Specific Report
```
Name: Weekly Report - Driver John
Type: Fuel Analysis
Frequency: Weekly
Format: Excel
Recipients: john.driver@company.com, supervisor@company.com
Filters: Vehicle #12345, Employee: John Smith
```

## 🎓 Advanced Tips

### Multiple Reports for Same Data
Create different reports with different formats:
- PDF for presentations
- Excel for analysis
Both for same data but different audiences.

### Test Before Schedule
Always click **"Run Now"** first to:
- Verify email delivery
- Check report content
- Confirm formatting
Then enable scheduled execution.

### Monitor Execution History
Check history weekly to:
- Ensure reports running successfully
- Identify any failures
- Track performance

### Backup Reports
Download important reports and save locally:
- Monthly reports for year-end review
- Audit trail documentation
- Comparison with previous periods

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Email not sending | Run `test_scheduled_reports.py` |
| No data in report | Check filters and date range |
| Schedule not working | Verify app is running and report enabled |
| Gmail rejected email | Use App Password |
| Report too large | Apply filters to reduce data |
| Wrong data | Check report type and filters |
| Execution failed | Check history for error message |

## 🔗 Additional Resources

- **Full Documentation**: `EMAIL_CONFIGURATION_GUIDE.md`
- **Implementation Details**: `SCHEDULED_REPORTS_IMPLEMENTATION.md`
- **Email Config Template**: `.env.example`
- **Test Script**: `test_scheduled_reports.py`

## ✅ Checklist

Before creating your first scheduled report:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Email configured in `.env` file
- [ ] Email tested (`python test_scheduled_reports.py`)
- [ ] Flask app running (`python app.py`)
- [ ] Logged in as admin
- [ ] Navigated to Analytics → Scheduled Reports

## 🎉 You're Ready!

Click **"Create New Report"** to get started with automated scheduled reports!

---

**Need help?** Check execution history for detailed error messages or refer to `EMAIL_CONFIGURATION_GUIDE.md` for setup instructions.
