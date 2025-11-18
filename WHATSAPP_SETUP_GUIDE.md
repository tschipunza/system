# WhatsApp Notifications Setup Guide

## Overview
The fleet management system now supports WhatsApp notifications via Twilio. Users can receive alerts for:
- Service overdue
- Service due soon
- Vehicle assignments
- Job card status updates
- Fuel expense alerts
- Daily summaries

## Setup Instructions

### 1. Get Twilio Account
1. Sign up at https://www.twilio.com/
2. Get a free trial account (includes $15 credit)
3. Find your credentials in the Twilio Console:
   - Account SID
   - Auth Token

### 2. Configure WhatsApp Sandbox (for testing)
1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Follow instructions to join your sandbox:
   - Send "join [your-sandbox-code]" to the provided WhatsApp number
   - Example: Send "join golden-tiger" to +1 415 523 8886
3. Note your sandbox WhatsApp number (e.g., whatsapp:+14155238886)

### 3. Configure System Settings
1. Log in to the fleet management system
2. Go to Settings → System Settings
3. Scroll to WhatsApp Settings section:
   - **Enable WhatsApp notifications**: Set to "true"
   - **Twilio Account SID**: Paste your Account SID
   - **Twilio Auth Token**: Paste your Auth Token
   - **Twilio WhatsApp sender**: Enter your sandbox number (e.g., whatsapp:+14155238886)
4. Click "Save Settings"

### 4. Set User Preferences
Each user should configure their notification preferences:
1. Go to Settings → Notifications
2. Enter your WhatsApp number (with country code, e.g., +263771234567)
3. Toggle which notifications you want via WhatsApp
4. Save preferences

### 5. Test the Integration
1. Go to Settings → Test WhatsApp
2. Enter your WhatsApp number
3. Select a message type (start with "Simple Test Message")
4. Click "Send Test Message"
5. Check your WhatsApp for the message

## Automatic Notification Triggers

The system automatically sends WhatsApp messages in these scenarios:

### 1. Service Notifications (Viewing Service Notifications Page)
- **Overdue**: Sent when you view the service notifications page and have overdue services
- **Due Soon**: Sent when services are within 1000 km or 7 days

### 2. Vehicle Assignment
- Sent immediately when a vehicle is assigned to an employee
- Employee receives details about the vehicle, purpose, and assignment date

### 3. Job Card Completion
- Sent when a job card status changes to "completed"
- Notifies the employee who worked on the job card

### 4. Fuel Expense Alert
- Sent when fuel price per liter exceeds the threshold (set in System Settings)
- Triggered when adding a fuel record

## Message Formats

### Service Overdue Alert
```
🚨 SERVICE OVERDUE ALERT

Vehicle: ABC-123
Make/Model: Toyota Hilux
Current Mileage: 105000 km
Service Due At: 100000 km
Overdue By: 5000 km

⚠️ This vehicle requires immediate service attention.

Fleet Management System
```

### Service Due Soon
```
⚠️ SERVICE DUE SOON

Vehicle: ABC-123
Make/Model: Toyota Hilux
Current Mileage: 99500 km
Service Due At: 100000 km
Remaining: 500 km

Please schedule service soon.

Fleet Management System
```

### Vehicle Assignment
```
🚗 VEHICLE ASSIGNMENT

Hello John Doe,

A vehicle has been assigned to you:

Vehicle: ABC-123
Make/Model: Toyota Hilux
Assignment Date: Today
Purpose: Field Work

Please take good care of the vehicle.

Fleet Management System
```

### Job Card Status
```
✅ JOB CARD UPDATE

Job Card: JC-2024-001
Vehicle: ABC-123
Status: COMPLETED

Fleet Management System
```

## Troubleshooting

### Messages Not Sending
1. **Check System Settings**: Verify WhatsApp is enabled and credentials are correct
2. **Check User Preferences**: Ensure the user has WhatsApp notifications enabled and a valid number entered
3. **Sandbox Registration**: For testing, make sure you've joined the Twilio sandbox
4. **Check Logs**: Look at the console output for error messages
5. **Twilio Console**: Check the Twilio logs for detailed error information

### Error: "Twilio credentials not configured"
- Make sure you've entered the Account SID, Auth Token, and sender number in System Settings

### Error: "Unable to create record: Twilio number is not registered"
- The recipient needs to join your Twilio sandbox first (for testing)
- For production, you need an approved Twilio number

### Phone Number Format
- Always include country code: +263771234567 (Zimbabwe), +1234567890 (USA)
- Don't include spaces or special characters except the + sign

## Production Deployment

For production use (beyond testing):

1. **Get Approved Sender Number**:
   - Request a Twilio number approved for WhatsApp
   - This requires business verification and can take 1-2 weeks
   - Update the sender number in System Settings

2. **Upgrade Twilio Account**:
   - Convert from trial to paid account
   - Add billing information
   - Costs: ~$0.005 per message (varies by country)

3. **Message Templates**:
   - For some countries, you may need pre-approved message templates
   - Check Twilio documentation for your region

## Code Structure

### Files
- `whatsapp_service.py` - Core WhatsApp sending functions
- `routes.py` - Notification triggers integrated into business logic
- `models_settings.py` - Database schema for settings and preferences
- `templates/notification_settings.html` - User preference UI
- `templates/test_whatsapp.html` - Testing interface

### Key Functions in whatsapp_service.py
- `send_whatsapp_message()` - Core sending function
- `send_service_overdue_alert()` - Service overdue notifications
- `send_service_due_soon_alert()` - Service due soon notifications
- `send_vehicle_assignment_alert()` - Vehicle assignment notifications
- `send_job_card_status_alert()` - Job card updates
- `send_fuel_expense_alert()` - Fuel cost alerts
- `send_daily_summary()` - Daily summaries (not yet triggered)

## Future Enhancements

Possible additions:
1. Scheduled daily summaries (cron job)
2. Bulk notifications for multiple vehicles
3. Two-way communication (reply to WhatsApp messages)
4. WhatsApp Business API integration
5. Message templates for compliance
6. Notification history/logs
7. Rate limiting to prevent spam

## Support

For issues or questions:
1. Check Twilio documentation: https://www.twilio.com/docs/whatsapp
2. Test using the Test WhatsApp page
3. Check system logs for detailed error messages
4. Review Twilio console logs

## Cost Estimate

With Twilio pricing (approximate):
- WhatsApp messages: $0.005 - $0.01 per message (varies by country)
- 100 notifications/day = ~$0.50 - $1.00/day = $15 - $30/month
- Free trial includes $15 credit for testing
