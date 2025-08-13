from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email, authority_name, verification_token):
    """
    Send email verification link using Mailtrap SMTP
    """
    smtp_config = {
        'host': current_app.config['MAILTRAP_HOST'],
        'port': current_app.config['MAILTRAP_PORT'],
        'username': current_app.config['MAILTRAP_USERNAME'],
        'password': current_app.config['MAILTRAP_PASSWORD'],
        'from_email': current_app.config['MAILTRAP_FROM_EMAIL']
    }

    # Create verification URL
    verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={verification_token}"

    # Email content
    subject = "Verify Your Authority Email"
    body = f"""
    Dear {authority_name},

    Thank you for registering with ServeX. Please verify your email address by clicking the link below:
    {verification_url}

    If you did not request this, please ignore this email.

    Best regards,
    ServeX Team
    """

    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from_email']
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Mailtrap SMTP server
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        current_app.logger.info(f"Verification email sent to {email}")
    except Exception as e:
        current_app.logger.error(f"Error sending email to {email}: {str(e)}")
        raise