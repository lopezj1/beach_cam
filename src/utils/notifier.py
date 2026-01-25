"""Email notification system"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import logging
import gc

def send_alert_email(object_count, alert_frame_path, video_url, timestamp):
    """Send email alert with detection information"""
    
    smtp_server = None
    try:
        # Validate environment variables
        smtp_host = os.getenv('EMAIL_SMTP_HOST')
        smtp_port = os.getenv('EMAIL_SMTP_PORT', '587')
        email_user = os.getenv('EMAIL_USERNAME')
        email_pass = os.getenv('EMAIL_PASSWORD')
        recipient = os.getenv('RECIPIENT_EMAIL')
        
        if not all([smtp_host, email_user, email_pass, recipient]):
            raise ValueError(f"Missing email config - Host: {smtp_host}, User: {email_user}, Recipient: {recipient}")
        
        # Create HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px;">
            <h2 style="color: #e74c3c;">Beach Cam Alert</h2>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Detection Count:</strong> {object_count} objects</p>
                <p><strong>Time:</strong> {timestamp}</p>
                <p><strong>Video:</strong> <a href="{video_url}" style="color: #007bff;">View Full Video</a></p>
            </div>
            <div style="margin: 20px 0;">
                <img src="cid:alert_frame" alt="Detection Frame" style="max-width: 100%; border-radius: 5px;">
            </div>
            <footer style="margin-top: 30px; font-size: 12px; color: #666;">
                <p>Beach Cam Monitoring System</p>
            </footer>
        </body>
        </html>
        """
        
        # Create message with alternative parts
        msg = MIMEMultipart('related')
        msg['Subject'] = f"Beach Cam Alert: {object_count} Objects Detected"
        msg['From'] = os.getenv('EMAIL_USERNAME')
        msg['To'] = os.getenv('RECIPIENT_EMAIL')
        
        # Create alternative part for HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Attach HTML body
        msg_alternative.attach(MIMEText(html_body, 'html'))
        
        # Attach alert image if it exists
        img_data = None
        if alert_frame_path and os.path.exists(alert_frame_path):
            try:
                # Read image
                with open(alert_frame_path, 'rb') as f:
                    img_data = f.read()
                
                if img_data:
                    image = MIMEImage(img_data, 'jpeg')
                    image.add_header('Content-ID', '<alert_frame>')
                    image.add_header('Content-Disposition', 'inline', filename='alert_frame.jpg')
                    msg.attach(image)
                    logging.info(f"Attached alert frame: {alert_frame_path} ({len(img_data)} bytes)")
                else:
                    logging.warning(f"Alert frame exists but is empty: {alert_frame_path}")
            except Exception as e:
                logging.warning(f"Could not attach image: {e}")
        
        # Send email with proper resource cleanup
        logging.info("Sending alert email")
        smtp_server = smtplib.SMTP(
            os.getenv('EMAIL_SMTP_HOST'), 
            int(os.getenv('EMAIL_SMTP_PORT', '587')),
            timeout=10
        )
        smtp_server.starttls()
        smtp_server.login(
            os.getenv('EMAIL_USERNAME'), 
            os.getenv('EMAIL_PASSWORD')
        )
        
        smtp_server.send_message(msg)
        logging.info("Alert email sent successfully")
        
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        raise
    finally:
        # Ensure SMTP connection is closed
        if smtp_server:
            try:
                smtp_server.quit()
            except Exception:
                smtp_server.close()
        
        # Clean up image data from memory
        gc.collect()
