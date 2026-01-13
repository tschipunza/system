"""
Email Configuration and Sending Utilities
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EmailService:
    """Service for sending emails with attachments"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.sender_email = os.environ.get('SENDER_EMAIL', self.smtp_username)
        self.sender_name = os.environ.get('SENDER_NAME', 'Fleet Management System')
        
    def send_email(self, to_emails, subject, body_html, attachments=None):
        """
        Send email with optional attachments
        
        Args:
            to_emails: List of recipient email addresses or comma-separated string
            subject: Email subject line
            body_html: HTML content of the email
            attachments: List of tuples [(filename, file_data, mimetype), ...]
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            print("⚠️  Email not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
            return False
        
        try:
            # Parse recipients
            if isinstance(to_emails, str):
                to_emails = [email.strip() for email in to_emails.split(',')]
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Add HTML body
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for filename, file_data, mimetype in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✓ Email sent to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            print(f"✗ Email send failed: {e}")
            return False
    
    def send_report_email(self, to_emails, report_name, report_data, file_format='excel'):
        """
        Send scheduled report via email
        
        Args:
            to_emails: Recipient email addresses
            report_name: Name of the report
            report_data: Report content (bytes)
            file_format: 'excel' or 'pdf'
        """
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = 'xlsx' if file_format == 'excel' else 'pdf'
        filename = f"{report_name}_{timestamp}.{extension}"
        
        # Create email body
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                    Scheduled Report: {report_name}
                </h2>
                
                <p>Hello,</p>
                
                <p>Your scheduled report <strong>{report_name}</strong> has been generated and is attached to this email.</p>
                
                <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Report:</strong> {report_name}</p>
                    <p style="margin: 5px 0;"><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p style="margin: 5px 0;"><strong>Format:</strong> {file_format.upper()}</p>
                </div>
                
                <p>Please find the report attached to this email.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #7f8c8d;">
                    This is an automated email from your Fleet Management System. 
                    If you wish to stop receiving these reports, please update your notification preferences in the system settings.
                </p>
            </div>
        </body>
        </html>
        """
        
        subject = f"Scheduled Report: {report_name} - {datetime.now().strftime('%B %d, %Y')}"
        
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if file_format == 'excel' else 'application/pdf'
        attachments = [(filename, report_data, mimetype)]
        
        return self.send_email(to_emails, subject, body_html, attachments)
    
    def send_test_email(self, to_email):
        """Send a test email to verify configuration"""
        subject = "Test Email - Fleet Management System"
        body_html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">Test Email</h2>
            <p>If you're reading this, your email configuration is working correctly!</p>
            <p style="color: #27ae60;"><strong>✓ Email system is functional</strong></p>
            <hr>
            <p style="font-size: 12px; color: #7f8c8d;">
                Fleet Management System - Automated Email Service
            </p>
        </body>
        </html>
        """
        return self.send_email([to_email], subject, body_html)


# Global email service instance
email_service = EmailService()
