import os
import pathlib
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Load environment variables
env_path = pathlib.Path('/Users/lewis_1/source code/AIAgent/.env')
print(f"\nTrying to load .env file from: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    print("\nContent of .env file:")
    with open(env_path, 'r') as f:
        print(f.read())

load_dotenv(dotenv_path=env_path)

def send_test_email():
    print("\nStarting email test...")
    
    # Get email configuration
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    username = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    receiver_email = os.getenv('REVIEWER_EMAIL')
    base_url = os.getenv('BASE_URL', 'http://localhost:8000')

    # Print configuration (hide password)
    print("\nEmail Configuration:")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Username: {username}")
    print(f"Receiver: {receiver_email}")

    try:
        # Setup Jinja2 template environment
        template_env = Environment(
            loader=FileSystemLoader('templates')
        )
        template = template_env.get_template('review_email.html')
        
        # Generate test URLs
        test_content = {
            'content_id': 'TEST-001',
            'content': 'This is a test tweet content. #AI #Crypto',
            'platform': 'Twitter',
            'scheduled_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'approve_url': f"{base_url}/action/approve",
            'reject_url': f"{base_url}/action/reject",
            'edit_url': f"{base_url}/action/edit"
        }
        
        # Render email template
        html_content = template.render(**test_content)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Test Email - Social Media Content Review'
        msg['From'] = username
        msg['To'] = receiver_email
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server and send email
        print("\nConnecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("Logging in...")
            server.login(username, password)
            print("Sending email...")
            server.send_message(msg)
            print("\nTest email sent successfully!")

    except Exception as e:
        print(f"\nError sending test email: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    send_test_email()
