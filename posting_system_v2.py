import os
import json
import logging
import openai
import time
import emoji
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from tweet_templates import get_template, get_joke
import random

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
        """Initialize posting system with real data sources"""
        try:
            load_dotenv()
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.config = self.get_default_config()
            self.tweet_memory = TweetMemory()
            logger.info("Enhanced posting system initialized with real data sources")
        except Exception as e:
            logger.error(f"Error initializing posting system: {str(e)}")
            raise

    def get_default_config(self):
        """Get default configuration with verified sources"""
        return {
            "content_rules": {
                "max_length": 280,
                "required_elements": ["Facts", "Source", "Context"],
                "tone": "informative_with_humor"
            },
            "verified_sources": {
                "crypto": ["CoinDesk", "The Block", "L2Beat", "DeFiLlama"],
                "ai": ["OpenAI Blog", "DeepMind Blog", "arXiv", "HuggingFace Blog"],
                "market": ["CoinGecko", "DefiLlama", "Messari", "Dune Analytics"]
            }
        }

    def handle_tweet_interaction(self, content, content_type):
        """Handle tweet creation with verified information and appropriate humor"""
        try:
            # Get appropriate template and joke
            template = get_template(content_type)
            joke = random.choice(get_joke(content_type))
            
            # Format tweet with real data and humor
            tweet = self._format_tweet(content, template, joke, content_type)
            
            # Store interaction
            self.tweet_memory.store_interaction(content, tweet)
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error handling tweet interaction: {str(e)}")
            return f"Error creating tweet: {str(e)}"

    def _format_tweet(self, content, template, joke, content_type):
        """Format tweet with verified information and appropriate humor"""
        try:
            # Extract key information using OpenAI
            prompt = f"""
            Extract key verified information from this content for a tweet:
            {content}
            
            Requirements:
            - Only include verifiable facts
            - Include source attribution
            - No speculation or unverified claims
            - Format appropriately for Twitter
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts verified information for tweets."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract information from response
            info = response.choices[0].message.content
            
            # Format tweet with template and joke
            tweet = template.replace("[WITTY_OBSERVATION]", joke)
            tweet = tweet.replace("[TECH_HUMOR]", joke)
            tweet = tweet.replace("[MARKET_JOKE]", joke)
            
            # Add extracted information
            tweet = tweet.replace("[VERIFIED_MARKET_DATA]", info)
            tweet = tweet.replace("[ACTUAL_NEWS_HEADLINE]", content.split('\n')[0])
            
            # Add timestamp
            current_time = datetime.now().strftime("%Y-%m-%d")
            tweet = tweet.replace("[TIMESTAMP]", current_time)
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting tweet: {str(e)}")
            raise

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
            "timestamp": datetime.now().isoformat()
        }
        
    def get_recent_interactions(self, limit=10):
        """Get recent tweet interactions"""
        sorted_interactions = sorted(
            self.interactions.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        return dict(sorted_interactions[:limit])
