import os
import json
import logging
import smtplib
import openai
import time
import ssl
import emoji
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostingSystem:
    def __init__(self):
        """Initialize posting system"""
        try:
            # Initialize OpenAI client
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            # Use default configuration
            self.config = self.get_default_config()
            logger.info("Using default configuration")
            
        except Exception as e:
            logger.error(f"Error initializing posting system: {str(e)}")
            raise

    def get_default_config(self):
        """Get default configuration"""
        return {
            "content_rules": {
                "min_length": 50,
                "max_length": 280,
                "required_elements": ["Topic", "Core Message", "Interactive Element"],
                "tone": "angry",
                "hashtags": {
                    "required": True,
                    "min_count": 1,
                    "max_count": 3
                },
                "min_engagement": 3,
                "max_retries": 3,
                "engagement_score": 6
            },
            "content_preferences": {
                "topics": ["AI Technology", "Programming Development", "Tech Innovation"],
                "style": "information-oriented",
                "emoji_usage": "high",
                "include_links": True
            }
        }

    def create_prompt_from_config(self, config, content_type):
        """Create prompt from configuration"""
        rules = config["content_rules"]
        prefs = config["content_preferences"]
        
        prompt = f"""Create a tweet following these requirements strictly:

1. Content Rules (all must be followed):
- Character limit: {rules['min_length']}-{rules['max_length']} characters
- Must include these elements with clear labels:
  Topic: (choose from: {', '.join(prefs['topics'])})
  Core Message: (express anger and frustration)
  Interactive Element: (include question or call to action)
- Tone: {rules['tone']} (express strong dissatisfaction)
- Must include {rules['hashtags']['min_count']}-{rules['hashtags']['max_count']} hashtags
- Must include at least 2 angry emojis (😠, 😡, 💢, etc.)

Example Format:
Topic: AI Technology
Core Message: Absolutely furious with the current state of AI development! 😠
Interactive Element: What's your worst experience with AI? Share your frustration!
#AIFrustration #TechRage 😡💢

Generate a complete tweet with all required elements. Content type: {content_type}"""

        return prompt

    def send_content_via_email(self, content):
        """Send generated content via email"""
        try:
            # Get email configuration from environment
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            reviewer_email = os.getenv('REVIEWER_EMAIL')

            # Log email configuration (without password)
            logger.info(f"Email Configuration:")
            logger.info(f"SMTP Server: {smtp_server}")
            logger.info(f"SMTP Port: {smtp_port}")
            logger.info(f"SMTP Username: {smtp_username}")
            logger.info(f"Reviewer Email: {reviewer_email}")

            if not all([smtp_server, smtp_port, smtp_username, smtp_password, reviewer_email]):
                logger.error("Missing required email configuration")
                return False

            # Format email content with timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            email_content = f"""[{timestamp}]
{content}

-------------------
"""
            # Create message
            msg = MIMEText(email_content, 'plain', 'utf-8')
            msg['Subject'] = f'Generated Tweet Preview - {timestamp}'
            msg['From'] = smtp_username
            msg['To'] = reviewer_email

            # Create secure SSL/TLS context with certificate verification disabled
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Send email with debug info
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            logger.info("Preview content sent via email successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending preview content via email: {str(e)}")
            return False

    def process_generated_content(self, content):
        """Process and distribute generated content"""
        try:
            if not content:
                logger.error("No content to process")
                return False

            # Send content via email
            if not self.send_content_via_email(content):
                logger.error("Failed to send content via email")
                return False

            logger.info("Content processed and distributed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing content: {str(e)}")
            return False

    def validate_content(self, content, config):
        """Validate content against configuration"""
        try:
            rules = config["content_rules"]
            
            # Check length
            content_length = len(content)
            if not (rules["min_length"] <= content_length <= rules["max_length"]):
                logger.warning(f"Content length invalid: current {content_length} chars, required {rules['min_length']}-{rules['max_length']} chars")
                return False
                
            # Check hashtags
            hashtags = [word for word in content.split() if word.startswith('#')]
            if rules["hashtags"]["required"]:
                hashtag_count = len(hashtags)
                if not (rules["hashtags"]["min_count"] <= hashtag_count <= rules["hashtags"]["max_count"]):
                    logger.warning(f"Hashtag count invalid: current {hashtag_count}, required {rules['hashtags']['min_count']}-{rules['hashtags']['max_count']}")
                    return False
                    
            # Check required elements
            required_prefixes = {
                "Topic": "Topic:",
                "Core Message": "Core Message:",
                "Interactive Element": "Interactive Element:"
            }
            
            for element, prefix in required_prefixes.items():
                if prefix not in content:
                    logger.warning(f'Missing required element: {element} (should include "{prefix}")')
                    return False

            # Check for emojis
            emoji_count = len([c for c in content if c in emoji.EMOJI_DATA])
            if emoji_count < 2:
                logger.warning("Not enough emojis in content")
                return False
                    
            logger.info("Content validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return False

    def generate_content(self, content_type='news'):
        """Generate content based on configuration"""
        try:
            # Use default configuration
            config = self.get_default_config()
            
            # Generate content using OpenAI
            prompt = self.create_prompt_from_config(config, content_type)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional social media content creator specializing in creating engaging, angry-toned tweets about technology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Validate the generated content
            if not self.validate_content(content, config):
                logger.error("Generated content failed validation")
                return False
                
            # Process and distribute the content
            if not self.process_generated_content(content):
                logger.error("Failed to process and distribute content")
                return False
                
            logger.info("Content generated and distributed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return False

    def generate_single_tweet(self):
        """Generate a single tweet using default configuration"""
        try:
            config = self.get_default_config()
            
            # Generate content using OpenAI
            prompt = self.create_prompt_from_config(config, 'tweet')
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional social media content creator specializing in creating engaging, angry-toned tweets about technology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Validate and send the content
            if self.validate_content(content, config):
                if self.send_content_via_email(content):
                    logger.info("Tweet generated and sent successfully")
                    return True
                else:
                    logger.error("Failed to send tweet via email")
                    return False
            else:
                logger.error("Generated content failed validation")
                return False
                
        except Exception as e:
            logger.error(f"Error generating single tweet: {str(e)}")
            return False

def main():
    """Main function"""
    try:
        posting_system = PostingSystem()
        posting_system.generate_single_tweet()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
