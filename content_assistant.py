import os
import uuid
import openai
import tweepy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

class ContentAssistant:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize Twitter
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.reviewer_email = os.getenv('REVIEWER_EMAIL')
        self.base_url = 'http://localhost:5001'

    def generate_content(self, prompt):
        """Generate content using OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful content creator that generates high-quality, engaging content suitable for social media."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return None

    def send_for_review(self, content, subject="New Content for Review"):
        """Send content for review via email with an edit interface."""
        content_id = str(uuid.uuid4())
        
        # Store content for later retrieval
        from app import pending_content
        pending_content[content_id] = {
            'text': content,
            'timestamp': datetime.now().isoformat()
        }
        
        # Create email with review link
        review_url = f"{os.getenv('BASE_URL')}/review/edit/{content_id}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Content Review Request</h2>
            <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0;">
                <h3>Content Preview:</h3>
                <p>{content}</p>
            </div>
            <p>Click below to review, edit, or regenerate the content:</p>
            <a href="{review_url}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">
                Review & Edit Content
            </a>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = self.reviewer_email
            
            text_part = MIMEText(f"Please review the content at: {review_url}", 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def post_to_twitter(self, content):
        """Post approved content to Twitter"""
        try:
            tweet = self.twitter_client.create_tweet(text=content)
            return tweet.data['id']
        except Exception as e:
            print(f"Error posting to Twitter: {str(e)}")
            return None

    def create_content_workflow(self, topic):
        """Complete content creation workflow"""
        print(f"\nStarting content workflow for topic: {topic}")
        
        # Step 1: Generate content
        prompt = f"Create an engaging tweet about {topic}. Keep it within Twitter's character limit."
        content = self.generate_content(prompt)
        if not content:
            return False
        
        print(f"\nGenerated content:\n{content}")
        
        # Step 2: Send for review
        if self.send_for_review(content, f"Review Tweet about {topic}"):
            print("\nContent sent for review. Check your email.")
        else:
            print("\nFailed to send content for review.")
            return False
        
        return True

def main():
    assistant = ContentAssistant()
    
    try:
        while True:
            print("\n=== Content Assistant Menu ===")
            print("1. Generate content for a topic")
            print("2. Input custom content directly")
            print("3. Exit")
            
            try:
                choice = input("\nEnter your choice (1-3): ")
            except EOFError:
                print("\nInput error. Exiting...")
                break
            
            if choice == "1":
                try:
                    topic = input("\nEnter the topic for content generation: ")
                    assistant.create_content_workflow(topic)
                except EOFError:
                    print("\nInput error. Returning to menu...")
                    continue
                
            elif choice == "2":
                print("\nEnter your content (press Enter twice to finish):")
                lines = []
                try:
                    while True:
                        line = input()
                        if line:
                            lines.append(line)
                        elif lines:  # Empty line and we have content
                            break
                except EOFError:
                    if not lines:
                        print("\nInput error. Returning to menu...")
                        continue
                
                content = "\n".join(lines)
                print("\nPreview of your content:")
                print("-" * 50)
                print(content)
                print("-" * 50)
                
                try:
                    if input("\nSend for review? (y/n): ").lower() == 'y':
                        if assistant.send_for_review(content, "Review Custom Content"):
                            print("\nContent sent for review. Check your email.")
                        else:
                            print("\nFailed to send content for review.")
                except EOFError:
                    print("\nInput error. Returning to menu...")
                    continue
            
            elif choice == "3":
                print("\nGoodbye!")
                break
            
            else:
                print("\nInvalid choice. Please try again.")
            
            try:
                if input("\nContinue with another content? (y/n): ").lower() != 'y':
                    print("\nGoodbye!")
                    break
            except EOFError:
                print("\nInput error. Exiting...")
                break
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Exiting...")
        
if __name__ == "__main__":
    main()
