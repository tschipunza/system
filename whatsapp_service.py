"""
WhatsApp Notification Service using Twilio
"""
from twilio.rest import Client
from app import get_db_connection

def get_setting(key, default=None):
    """Get system setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key,))
        result = cursor.fetchone()
        return result['setting_value'] if result else default
    finally:
        cursor.close()
        conn.close()

def send_whatsapp_message(to_number, message):
    """
    Send WhatsApp message using Twilio
    
    Args:
        to_number: Recipient WhatsApp number (with country code, e.g., +263771234567)
        message: Message text to send
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Check if WhatsApp is enabled
        if get_setting('whatsapp_api_enabled') != 'true':
            print("WhatsApp notifications are disabled")
            return False
        
        # Get Twilio credentials
        account_sid = get_setting('twilio_account_sid')
        auth_token = get_setting('twilio_auth_token')
        from_number = get_setting('twilio_whatsapp_from')
        
        if not account_sid or not auth_token or not from_number:
            print("Twilio credentials not configured")
            return False
        
        # Format numbers for WhatsApp
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'
        
        # Send message via Twilio
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_number,
            body=message,
            to=to_number
        )
        
        print(f"WhatsApp message sent successfully. SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False

def send_service_overdue_alert(vehicle_number, vehicle_details, recipient_number):
    """Send service overdue WhatsApp alert"""
    message = f"""
🚨 *SERVICE OVERDUE ALERT*

Vehicle: *{vehicle_number}*
Make/Model: {vehicle_details.get('make')} {vehicle_details.get('model')}
Current Mileage: {vehicle_details.get('current_mileage', 'N/A')} km
Service Due At: {vehicle_details.get('service_due_mileage', 'N/A')} km
Overdue By: {vehicle_details.get('overdue_km', 'N/A')} km

⚠️ This vehicle requires immediate service attention.

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)

def send_service_due_soon_alert(vehicle_number, vehicle_details, recipient_number):
    """Send service due soon WhatsApp alert"""
    message = f"""
⚠️ *SERVICE DUE SOON*

Vehicle: *{vehicle_number}*
Make/Model: {vehicle_details.get('make')} {vehicle_details.get('model')}
Current Mileage: {vehicle_details.get('current_mileage', 'N/A')} km
Service Due At: {vehicle_details.get('service_due_mileage', 'N/A')} km
Remaining: {vehicle_details.get('km_remaining', 'N/A')} km

Please schedule service soon.

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)

def send_vehicle_assignment_alert(vehicle_number, vehicle_details, employee_name, recipient_number):
    """Send vehicle assignment WhatsApp notification"""
    message = f"""
🚗 *VEHICLE ASSIGNMENT*

Hello {employee_name},

A vehicle has been assigned to you:

Vehicle: *{vehicle_number}*
Make/Model: {vehicle_details.get('make')} {vehicle_details.get('model')}
Assignment Date: {vehicle_details.get('assignment_date')}
Purpose: {vehicle_details.get('purpose', 'N/A')}

Please take good care of the vehicle.

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)

def send_job_card_status_alert(job_card_number, status, vehicle_number, recipient_number):
    """Send job card status update WhatsApp notification"""
    status_emoji = {
        'open': '📋',
        'in_progress': '🔧',
        'on_hold': '⏸️',
        'completed': '✅',
        'cancelled': '❌'
    }
    
    message = f"""
{status_emoji.get(status, '📋')} *JOB CARD UPDATE*

Job Card: *{job_card_number}*
Vehicle: {vehicle_number}
Status: *{status.upper()}*

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)

def send_fuel_expense_alert(vehicle_number, fuel_cost, threshold, recipient_number):
    """Send fuel expense alert WhatsApp notification"""
    message = f"""
⛽ *FUEL EXPENSE ALERT*

Vehicle: *{vehicle_number}*
Fuel Cost: ${fuel_cost}
Threshold: ${threshold}

⚠️ Fuel cost exceeded alert threshold.

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)

def send_daily_summary(summary_data, recipient_number):
    """Send daily summary WhatsApp notification"""
    message = f"""
📊 *DAILY FLEET SUMMARY*

Date: {summary_data.get('date')}

🚗 Vehicles:
- Active: {summary_data.get('active_vehicles', 0)}
- In Service: {summary_data.get('in_service', 0)}

⛽ Fuel:
- Total Records: {summary_data.get('fuel_records', 0)}
- Total Cost: ${summary_data.get('fuel_cost', 0)}

🔧 Service:
- Overdue: {summary_data.get('overdue_service', 0)}
- Due Soon: {summary_data.get('due_soon', 0)}

📝 Job Cards:
- Open: {summary_data.get('open_jobs', 0)}
- Completed Today: {summary_data.get('completed_today', 0)}

Fleet Management System
    """.strip()
    
    return send_whatsapp_message(recipient_number, message)
