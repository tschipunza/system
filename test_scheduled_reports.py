"""
Test Email Configuration for Scheduled Reports System
Run this script to verify email settings before using scheduled reports
"""

import os
import sys

def test_email_configuration():
    """Test email configuration and send a test email"""
    
    print("=" * 60)
    print("Scheduled Reports Email Configuration Test")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("1. Checking environment variables...")
    required_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SENDER_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if 'PASSWORD' in var:
                print(f"   ✓ {var}: {'*' * len(value)}")
            else:
                print(f"   ✓ {var}: {value}")
        else:
            print(f"   ✗ {var}: NOT SET")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these variables in your .env file or environment.")
        print("See .env.example for a template.")
        return False
    
    # Import email service
    print("2. Importing email service...")
    try:
        from email_service import EmailService
        print("   ✓ Email service imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import email service: {e}")
        return False
    
    print()
    
    # Get recipient email
    print("3. Enter test email recipient:")
    recipient = input("   Email address: ").strip()
    
    if not recipient or '@' not in recipient:
        print("   ✗ Invalid email address")
        return False
    
    print()
    
    # Send test email
    print("4. Sending test email...")
    try:
        email_service = EmailService()
        success = email_service.send_test_email(recipient)
        
        if success:
            print("   ✓ Test email sent successfully!")
            print()
            print("=" * 60)
            print("✓ Email configuration is working correctly!")
            print("=" * 60)
            print()
            print(f"Check {recipient} for the test email.")
            print("If you don't receive it, check your spam folder.")
            return True
        else:
            print("   ✗ Failed to send test email")
            print()
            print("=" * 60)
            print("❌ Email configuration test failed")
            print("=" * 60)
            print()
            print("Common issues:")
            print("1. Gmail: Ensure 2FA is enabled and you're using an App Password")
            print("2. Check SMTP server and port are correct")
            print("3. Verify firewall allows SMTP connections")
            print("4. Check credentials are correct")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print()
        print("=" * 60)
        print("❌ Email configuration test failed")
        print("=" * 60)
        print()
        print(f"Error details: {e}")
        return False

def check_scheduler_setup():
    """Check if scheduler is properly configured"""
    print()
    print("=" * 60)
    print("Scheduler Configuration Check")
    print("=" * 60)
    print()
    
    print("Checking scheduler components...")
    
    # Check scheduler.py exists
    if os.path.exists('scheduler.py'):
        print("   ✓ scheduler.py found")
    else:
        print("   ✗ scheduler.py not found")
        return False
    
    # Check email_service.py exists
    if os.path.exists('email_service.py'):
        print("   ✓ email_service.py found")
    else:
        print("   ✗ email_service.py not found")
        return False
    
    # Try importing
    try:
        from scheduler import scheduled_reports_manager
        print("   ✓ Scheduler imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import scheduler: {e}")
        return False
    
    # Check APScheduler is installed
    try:
        import apscheduler
        print(f"   ✓ APScheduler {apscheduler.__version__} installed")
    except ImportError:
        print("   ✗ APScheduler not installed")
        print()
        print("Install APScheduler: pip install apscheduler==3.11.1")
        return False
    
    print()
    print("=" * 60)
    print("✓ Scheduler setup is correct!")
    print("=" * 60)
    return True

def main():
    """Main test function"""
    print()
    
    # Check scheduler setup
    scheduler_ok = check_scheduler_setup()
    
    if not scheduler_ok:
        print()
        print("Fix scheduler issues before testing email configuration.")
        sys.exit(1)
    
    # Test email configuration
    print()
    email_ok = test_email_configuration()
    
    if email_ok:
        print()
        print("Next steps:")
        print("1. Start the Flask application")
        print("2. Log in as admin")
        print("3. Navigate to Analytics > Scheduled Reports")
        print("4. Create a test scheduled report")
        print("5. Click 'Run Now' to test report generation and email delivery")
        print()
        sys.exit(0)
    else:
        print()
        print("Please fix email configuration issues before using scheduled reports.")
        print("See EMAIL_CONFIGURATION_GUIDE.md for detailed instructions.")
        print()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Test cancelled by user")
        sys.exit(1)
