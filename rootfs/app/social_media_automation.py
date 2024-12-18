import os
import schedule
import time
from datetime import datetime
import openai
from dotenv import load_dotenv
import tweepy
import requests
import json
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from jose import jwt
import base64
from pathlib import Path
from content_strategy_manager import ContentStrategyManager

# Load environment variables
load_dotenv()

class EmailReviewSystem:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.reviewer_email = os.getenv('REVIEWER_EMAIL')
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
        
        # Setup Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader('templates')
        )
        
    def generate_action_token(self, action, content_id):
        """Generate JWT token for email actions"""
        payload = {
            'action': action,
            'content_id': content_id,
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hour expiration
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def generate_action_url(self, action, content_id):
        """Generate action URL with JWT token"""
        token = self.generate_action_token(action, content_id)
        return f"{self.base_url}/action/{token}"
    
    def send_review_email(self, content_id, content, platform, scheduled_time):
        """Send review email with approve/reject/edit buttons"""
        template = self.template_env.get_template('review_email.html')
        
        # Generate action URLs
        approve_url = self.generate_action_url('approve', content_id)
        reject_url = self.generate_action_url('reject', content_id)
        edit_url = self.generate_action_url('edit', content_id)
        
        # Render email template
        html_content = template.render(
            content_id=content_id,
            content=content,
            platform=platform,
            scheduled_time=scheduled_time,
            approve_url=approve_url,
            reject_url=reject_url,
            edit_url=edit_url
        )
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'社交媒体内容审核 #{content_id}'
        msg['From'] = self.smtp_username
        msg['To'] = self.reviewer_email
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                print(f"Review email sent for content #{content_id}")
        except Exception as e:
            print(f"Error sending review email: {e}")

class SocialMediaAutomation:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize Twitter API
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        self.twitter_api = tweepy.API(auth)
        
        # Initialize email review system
        self.email_review = EmailReviewSystem()
        
        # Initialize Zapier webhooks
        self.zapier_webhooks = {
            'content_generated': os.getenv('ZAPIER_WEBHOOK_CONTENT_GENERATED'),
            'content_approved': os.getenv('ZAPIER_WEBHOOK_CONTENT_APPROVED'),
            'content_rejected': os.getenv('ZAPIER_WEBHOOK_CONTENT_REJECTED'),
            'content_published': os.getenv('ZAPIER_WEBHOOK_CONTENT_PUBLISHED'),
            'auto_approved': os.getenv('ZAPIER_WEBHOOK_AUTO_APPROVED')
        }
        
        # Initialize content strategy manager
        self.strategy_manager = ContentStrategyManager()
        
        # Initialize database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('content.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contents
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             text TEXT NOT NULL,
             platform TEXT NOT NULL,
             scheduled_time TEXT NOT NULL,
             status TEXT DEFAULT 'pending',
             created_at TEXT NOT NULL)
        ''')
        conn.commit()
        conn.close()

    def generate_content(self, platform='twitter'):
        """Generate content using ChatGPT based on content strategy"""
        try:
            # Get content prompt from strategy manager
            prompt = self.strategy_manager.get_content_prompt(platform)
            
            # Generate content using ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media expert who creates engaging content for the target audience."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            
            # Get relevant hashtags
            hashtags = self.strategy_manager.get_hashtags()
            
            # Add hashtags to content
            content_with_hashtags = f"{content}\n\n{' '.join(hashtags)}"
            
            # Evaluate content
            evaluation = self.strategy_manager.evaluate_content(content_with_hashtags, platform)
            
            if all(evaluation.values()):
                return content_with_hashtags
            else:
                print(f"Content evaluation failed: {evaluation}")
                return None
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def save_content_for_review(self, content, platform, scheduled_time):
        """Save content to database and send for review"""
        conn = sqlite3.connect('content.db')
        c = conn.cursor()
        
        # Save to database
        c.execute('''
            INSERT INTO contents (text, platform, scheduled_time, created_at)
            VALUES (?, ?, ?, ?)
        ''', (content, platform, scheduled_time, datetime.now().isoformat()))
        
        content_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Send for email review
        self.email_review.send_review_email(
            content_id,
            content,
            platform,
            scheduled_time
        )
        
        # Trigger Zapier webhook for content generation
        self.trigger_zapier_webhook('content_generated', {
            'content_id': content_id,
            'content': content,
            'platform': platform,
            'scheduled_time': scheduled_time
        })
        
        return content_id

    def post_approved_content(self):
        """Post approved content"""
        conn = sqlite3.connect('content.db')
        c = conn.cursor()
        
        now = datetime.now().strftime('%Y-%m-%d %H:00:00')
        c.execute('''
            SELECT * FROM contents 
            WHERE (status = "approved" OR 
                  (status = "pending" AND datetime(created_at, '+24 hours') <= datetime('now')))
            AND scheduled_time <= ? 
            AND scheduled_time > datetime(?, "-1 hour")
        ''', (now, now))
        
        contents = c.fetchall()
        for content in contents:
            content_id, text, platform, scheduled_time, status, created_at = content
            
            if platform == 'twitter':
                try:
                    self.twitter_api.update_status(text)
                    print(f"Successfully posted to Twitter: {text}")
                    
                    # Update status to posted
                    c.execute('UPDATE contents SET status = "posted" WHERE id = ?', (content_id,))
                    
                    # Trigger Zapier webhook for published content
                    webhook_type = 'auto_approved' if status == 'pending' else 'content_published'
                    self.trigger_zapier_webhook(webhook_type, {
                        'content_id': content_id,
                        'content': text,
                        'platform': platform,
                        'published_time': datetime.now().isoformat(),
                        'auto_approved': status == 'pending'
                    })
                    
                    if status == "pending":
                        print(f"Content #{content_id} was auto-approved after 24 hours")
                except Exception as e:
                    print(f"Error posting to Twitter: {e}")
        
        conn.commit()
        conn.close()

    def analyze_audience(self):
        """Analyze target audience using TweetHunter"""
        try:
            url = "https://api.tweethunter.io/api/v1/audience/analyze"
            response = requests.post(url, headers={
                'Authorization': f'Bearer {os.getenv("TWEETHUNTER_API_KEY")}',
                'Content-Type': 'application/json'
            })
            return response.json()
        except Exception as e:
            print(f"Error analyzing audience: {e}")
            return None

    def schedule_content(self):
        """Generate and schedule content for review based on strategy"""
        # Get current platform from strategy
        platform = 'twitter'  # Can be expanded based on strategy
        
        content = self.generate_content(platform)
        if content:
            # Get next available slot based on content type
            next_slot = datetime.now().replace(minute=0, second=0, microsecond=0)
            next_slot = next_slot.strftime('%Y-%m-%d %H:00:00')
            
            # Save for review
            content_id = self.save_content_for_review(content, platform, next_slot)
            print(f"Content #{content_id} saved and sent for review")
            
            # Update performance metrics
            self.strategy_manager.update_performance_metrics({
                'engagement_rate': 0.02,  # Example values
                'click_through_rate': 0.01,
                'follower_growth': 0.05
            })

    def trigger_zapier_webhook(self, webhook_type, data):
        """Trigger a Zapier webhook with data"""
        webhook_url = self.zapier_webhooks.get(webhook_type)
        if webhook_url:
            try:
                response = requests.post(webhook_url, json=data)
                if response.status_code == 200:
                    print(f"Successfully triggered Zapier webhook: {webhook_type}")
                else:
                    print(f"Failed to trigger Zapier webhook: {webhook_type}")
            except Exception as e:
                print(f"Error triggering Zapier webhook: {e}")

def main():
    automation = SocialMediaAutomation()
    
    # Schedule content generation
    schedule.every().day.at("09:00").do(automation.schedule_content)
    schedule.every().day.at("15:00").do(automation.schedule_content)
    schedule.every().day.at("20:00").do(automation.schedule_content)
    
    # Check for approved content every hour
    schedule.every().hour.do(automation.post_approved_content)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
