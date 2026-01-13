# Scheduled Reports Email Configuration Guide

## Overview
The scheduled reports system sends automated reports via email. This guide explains how to configure email settings.

## Email Configuration

### Environment Variables
Create a `.env` file in the root directory or set these environment variables:

```env
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Fleet Management System
```

### Gmail Configuration

#### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Navigate to Security > 2-Step Verification
- Enable 2-Factor Authentication

#### 2. Generate App Password
- Go to Security > App passwords
- Select "Mail" as the app
- Select "Other" as the device and enter "Fleet Management"
- Copy the 16-character password
- Use this password for `SMTP_PASSWORD`

### Other Email Providers

#### Microsoft Outlook/Office 365
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### Custom SMTP Server
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Testing Email Configuration

### Method 1: Test Email Route
1. Start the Flask application
2. Log in as admin
3. Navigate to Analytics > Scheduled Reports
4. Create a test report with your email
5. Click "Run Now" to test email delivery

### Method 2: Python Script
Create a test file `test_email.py`:

```python
from email_service import EmailService
import os

# Set environment variables
os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SMTP_USERNAME'] = 'your-email@gmail.com'
os.environ['SMTP_PASSWORD'] = 'your-app-password'
os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'

# Test email
email_service = EmailService()
success = email_service.send_test_email('recipient@example.com')

if success:
    print("✓ Email sent successfully!")
else:
    print("✗ Email failed to send")
```

Run: `python test_email.py`

## Scheduled Reports Features

### Report Types
- **Fuel Analysis**: Fuel consumption, costs, and efficiency metrics
- **Maintenance Costs**: Service and maintenance expenses by vehicle
- **Vehicle Assignments**: Current and historical vehicle assignments

### Schedules
- **Daily**: Runs every day at 8:00 AM
- **Weekly**: Runs every Monday at 8:00 AM
- **Monthly**: Runs on the 1st of each month at 8:00 AM

### Report Formats
- **Excel (XLSX)**: Spreadsheet with formatted data, headers, and auto-width columns
- **PDF**: Professional report with company branding, tables, and charts

## Creating Scheduled Reports

### Step 1: Navigate to Scheduled Reports
- Log in as admin
- Go to Analytics menu
- Click "Scheduled Reports"

### Step 2: Create New Report
- Click "Create New Report"
- Fill in report details:
  - Report Name (descriptive name)
  - Report Type (fuel, maintenance, assignments)
  - Frequency (daily, weekly, monthly)
  - Format (Excel or PDF)
  - Email recipients (comma-separated)

### Step 3: Apply Filters (Optional)
- Select specific vehicles
- Select specific employees
- Leave unchecked to include all

### Step 4: Save and Activate
- Click "Create Scheduled Report"
- Report will start running on schedule
- Use "Run Now" to test immediately

## Managing Reports

### View Reports
- List shows all scheduled reports
- Status: Active/Inactive
- Next run date and time
- Execution count

### Actions
- **Run Now**: Execute report immediately
- **History**: View execution log with status and errors
- **Disable/Enable**: Pause/resume scheduled execution
- **Delete**: Remove report and stop scheduling

### Execution History
- Execution timestamp
- Success/failure status
- Duration in seconds
- Number of records
- Error messages (if failed)

## Troubleshooting

### Email Not Sending
1. Check environment variables are set correctly
2. Verify SMTP credentials
3. Check SMTP port (587 for TLS, 465 for SSL)
4. Ensure firewall allows SMTP connections
5. Check execution history for error messages

### Gmail Specific Issues
- Ensure 2FA is enabled
- Use App Password, not regular password
- Check "Less secure app access" is disabled (use App Password instead)
- Verify account isn't blocked by Google

### Report Generation Errors
1. Check database connectivity
2. Verify data exists for selected filters
3. Review execution history for detailed error
4. Check file permissions for report output

### Schedule Not Running
1. Ensure Flask app is running
2. Check scheduler is initialized in logs
3. Verify report is active (not disabled)
4. Check next_run_date is in the future

## Best Practices

### Email Configuration
- Use dedicated email account for reports
- Keep SMTP credentials secure
- Use environment variables, never hardcode
- Test configuration before production

### Report Scheduling
- Schedule during off-peak hours
- Start with weekly reports, adjust as needed
- Include multiple recipients for redundancy
- Use descriptive report names

### Data Management
- Apply filters to reduce report size
- Export large datasets to Excel
- Use PDF for presentation-quality reports
- Review execution history regularly

### Performance
- Limit concurrent scheduled reports
- Monitor execution duration
- Archive old execution logs periodically
- Optimize filters for large datasets

## Security Considerations

### Email Security
- Use TLS/SSL for SMTP connections
- Never commit credentials to version control
- Rotate passwords regularly
- Use dedicated service account

### Report Access
- Only admins can create scheduled reports
- Recipients must have valid email addresses
- Reports contain sensitive business data
- Consider encrypting PDF reports

### Data Privacy
- Comply with data protection regulations
- Include privacy notice in emails
- Limit data exposure with filters
- Log all report access and delivery

## Support

For issues or questions:
1. Check execution history for error details
2. Review application logs
3. Test email configuration separately
4. Verify database connectivity
5. Contact system administrator

## Example Configuration

Complete `.env` file example:

```env
# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-db-password
MYSQL_DATABASE=flask_auth_db

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=fleet.reports@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SENDER_EMAIL=fleet.reports@gmail.com
SENDER_NAME=Fleet Management System

# Multi-Tenant
MULTI_TENANT_ENABLED=true
```

## Maintenance

### Regular Tasks
- Monitor execution success rate
- Review and clean execution logs (keep 90 days)
- Update email recipients as needed
- Adjust schedules based on usage
- Test email configuration after updates

### Monitoring
- Check scheduler status on app startup
- Review failed executions daily
- Monitor email delivery rates
- Track report generation duration
- Alert on consecutive failures
