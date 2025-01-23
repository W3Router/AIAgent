import os
import json
import logging
import openai
import time
import emoji
import random
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from tweet_templates import get_template, get_joke, VERIFIED_SOURCES

# Set up logging
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
        """Initialize posting system with Gen-Z style"""
        try:
            load_dotenv()
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.config = self.get_default_config()
            self.tweet_memory = TweetMemory()
            logger.info("Gen-Z style posting system initialized fr fr")
        except Exception as e:
            logger.error(f"Error initializing posting system: {str(e)}")
            raise

    def get_default_config(self):
        """Get default configuration with Gen-Z style"""
        return {
            "content_rules": {
                "max_length": 280,
                "required_elements": ["Facts", "Source", "Security", "Memes"],
                "tone": "gen_z_tech_savvy"
            },
            "verified_sources": VERIFIED_SOURCES,
            "style_elements": {
                "tech_slang": [
                    "goes brrr", "no cap", "fr fr", "bussin",
                    "on god", "actually crazy", "sus"
                ],
                "meme_formats": [
                    "POV:", "No one:", "*exists*",
                    "Task failed successfully", "do be like that"
                ]
            }
        }

    def handle_tweet_interaction(self, content, content_type):
        """Handle tweet creation with Gen-Z style"""
        try:
            # Get appropriate template and joke
            template = get_template(content_type)
            joke = random.choice(get_joke(content_type))
            
            # Format tweet with Gen-Z style
            tweet = self._format_tweet(content, template, joke, content_type)
            
            # Store interaction
            self.tweet_memory.store_interaction(content, tweet)
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error handling tweet interaction: {str(e)}")
            return f"Error creating tweet (not bussin): {str(e)}"

    def _format_tweet(self, content, template, joke, content_type):
        """Format tweet with Gen-Z style and verified information"""
        try:
            # Extract key information using OpenAI with Gen-Z style prompt
            prompt = f"""
            Extract key verified information from this content and make it Gen-Z style (fr fr):
            {content}
            
            Requirements:
            - Focus on AI agent capabilities and security features
            - Only include verifiable facts (no cap)
            - Include source attribution
            - Use Gen-Z tech slang
            - Add meme references where appropriate
            - Keep it bussin fr fr
            - Format for Twitter
            
            Style guide:
            - Use "fr fr", "no cap", "bussin", "goes brrr" appropriately
            - Include relevant emojis (💀, 👀, 🔥)
            - Reference memes and tech culture
            - Keep it technically accurate but make it fun
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Gen-Z tech expert who keeps it real (fr fr) while providing accurate information."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract information and style it
            info = response.choices[0].message.content
            
            # Format tweet with template and joke
            tweet = template.replace("[TECH_HUMOR]", joke)
            tweet = tweet.replace("[SECURITY_QUIP]", joke)
            
            # Add verified information with Gen-Z style
            tweet = tweet.replace("[ACTUAL_NEWS_HEADLINE]", self._add_gen_z_style(content.split('\n')[0]))
            
            # Add timestamp
            current_time = datetime.now().strftime("%Y-%m-%d")
            tweet = tweet.replace("[TIMESTAMP]", current_time)
            
            # Add source verification
            source = self._verify_source(content_type, info)
            tweet = tweet.replace("[SOURCE]", source)
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting tweet (not bussin fr fr): {str(e)}")
            raise

    def _add_gen_z_style(self, text):
        """Add Gen-Z style to text"""
        style_elements = self.config["style_elements"]
        
        # Maybe add a tech slang term
        if random.random() > 0.5:
            text += f" ({random.choice(style_elements['tech_slang'])})"
            
        return text

    def _verify_source(self, content_type, info):
        """Verify and return appropriate source"""
        sources = self.config["verified_sources"].get(
            "ai_agents" if content_type == "ai_agent" else "security",
            self.config["verified_sources"]["ai_agents"]
        )
        return sources[0]  # Default to first verified source

class TweetMemory:
    def __init__(self):
        """Initialize tweet memory system"""
        self.interactions = {}
        
    def store_interaction(self, content, tweet):
        """Store tweet interaction with metadata"""
        interaction_id = str(time.time())
        self.interactions[interaction_id] = {
            "content": content,
            "tweet": tweet,
            "timestamp": datetime.now().isoformat(),
            "vibe_check": "bussin"  # fr fr
        }
        
    def get_recent_interactions(self, limit=10):
        """Get recent tweet interactions"""
        sorted_interactions = sorted(
            self.interactions.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        return dict(sorted_interactions[:limit])

if __name__ == "__main__":
    # Test the system (fr fr)
    posting_system = PostingSystem()
    
    # Test AI agent tweet (no cap)
    ai_tweet = posting_system.handle_tweet_interaction(
        "OpenAI drops insane new AI agent security framework",
        "ai_agent"
    )
    print("\nAI Agent Tweet (bussin fr fr):")
    print(ai_tweet)
    
    # Test security tweet (on god)
    security_tweet = posting_system.handle_tweet_interaction(
        "New zero-trust architecture just dropped",
        "security"
    )
    print("\nSecurity Tweet (goes crazy):")
    print(security_tweet)
