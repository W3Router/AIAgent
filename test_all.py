import os
import tweepy
import smtplib
import openai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"\nTrying to load .env file from: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}")
    load_dotenv(env_path)
    print("Environment variables loaded successfully")

def test_email():
    print("\n=== Testing Email Configuration ===")
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    reviewer_email = os.getenv('REVIEWER_EMAIL')
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"From/To Email: {smtp_username}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = reviewer_email
        msg['Subject'] = "Test Email from Integration Test"
        
        body = f"This is a test email sent at {datetime.now()}"
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        print("\nConnecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login
        print("Logging in to SMTP server...")
        server.login(smtp_username, smtp_password)
        
        # Send email
        print("Sending email...")
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error in email test: {str(e)}")
        raise

def test_twitter():
    print("\n=== Testing Twitter API ===")
    
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    try:
        # Test OAuth 1.0a Authentication
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        print("\nTesting OAuth 1.0a authentication...")
        user = api.verify_credentials()
        print(f"Successfully authenticated as: @{user.screen_name}")
        
        # Test OAuth 2.0 (Bearer Token) Authentication
        print("\nTesting Bearer Token authentication...")
        client = tweepy.Client(bearer_token=bearer_token,
                             consumer_key=api_key,
                             consumer_secret=api_secret,
                             access_token=access_token,
                             access_token_secret=access_token_secret)
        
        me = client.get_me()
        print(f"Successfully retrieved user data using Bearer Token")
        print(f"User ID: {me.data.id}")
        print(f"Username: @{me.data.username}")
        print(f"Name: {me.data.name}")
        
        # Test creating a tweet (optional)
        # tweet = client.create_tweet(text=f"Test tweet from integration test at {datetime.now()}")
        # print(f"\nSuccessfully posted test tweet!")
        
    except Exception as e:
        print(f"Error in Twitter test: {str(e)}")
        raise

def test_openai():
    print("\n=== Testing OpenAI API ===")
    
    api_key = os.getenv('OPENAI_API_KEY')
    openai.api_key = api_key
    
    try:
        print("Testing OpenAI API with a simple completion...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, testing OpenAI API!' in a creative way."}
            ]
        )
        
        print("\nAPI Response:")
        print(response.choices[0].message.content)
        print("\nOpenAI API test successful!")
        
    except Exception as e:
        print(f"Error in OpenAI test: {str(e)}")
        raise

def main():
    print("Starting integration tests...")
    load_env()
    
    try:
        # Test Email
        test_email()
        print("\n✅ Email test passed!")
        
        # Test Twitter
        test_twitter()
        print("\n✅ Twitter API test passed!")
        
        # Test OpenAI
        test_openai()
        print("\n✅ OpenAI API test passed!")
        
        print("\n🎉 All integration tests passed successfully! 🎉")
        
    except Exception as e:
        print(f"\n❌ Integration tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
