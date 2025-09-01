from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import secrets

def send_verification_email(email, authority_name, verification_token, is_authority):
    """
    Send email verification link using Mailtrap SMTP
    """
    try:
        smtp_config = {
            'host': current_app.config['MAILTRAP_HOST'],
            'port': current_app.config['MAILTRAP_PORT'],
            'username': current_app.config['MAILTRAP_USERNAME'],
            'password': current_app.config['MAILTRAP_PASSWORD'],
            'from_email': current_app.config['MAILTRAP_FROM_EMAIL']
        }
        type_param = 'authority' if is_authority else 'admin'
        # Create verification URL
        verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?type={type_param}&token={verification_token}"

        # Email content
        subject = "Verify Your ServeX Email"
        body = f"""
            Dear {authority_name},

            Thank you for registering with ServeX. Please verify your email address by clicking the link below:
            {verification_url}

            If you did not request this, please ignore this email.

            Best regards,
            ServeX Team
            """
        print(f"Sending verification email to {body}")
        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Mailtrap SMTP server
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        current_app.logger.info(f"Verification email sent to {email}")
    except Exception as e:
        current_app.logger.error(f"Error sending email to {email}: {str(e)}")
        raise e
    
def send_password_email(email, authority_name):
    """
    Send a system-generated 8-character random password to the specified email
    Returns the generated password
    """
    try:
        # Generate 8-character random password
        characters = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(characters) for _ in range(8))

        smtp_config = {
            'host': current_app.config['MAILTRAP_HOST'],
            'port': current_app.config['MAILTRAP_PORT'],
            'username': current_app.config['MAILTRAP_USERNAME'],
            'password': current_app.config['MAILTRAP_PASSWORD'],
            'from_email': current_app.config['MAILTRAP_FROM_EMAIL']
        }

        # Email content
        subject = "Your ServeX Account Password"
        body = f"""
            Dear {authority_name},

            Your new ServeX account password is: {password}

            Please use this password to log in to your account. We recommend changing it after your first login.

            If you did not request this password, please contact our support team immediately.

            Best regards,
            ServeX Team
            """

        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Mailtrap SMTP server
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        current_app.logger.info(f"Password email sent to {email}")
        return password

    except Exception as e:
        current_app.logger.error(f"Error sending password email to {email}: {str(e)}")
        raise e