import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from real_crypto_news import CryptoNewsAggregator, generate_tweet

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_posts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIPostingSystem:
    def __init__(self):
        """Initialize AI posting system"""
        try:
            load_dotenv()
            self.news_aggregator = CryptoNewsAggregator()
            self.last_post_date = None
            self.posting_hour = 10  # Post at 10 AM every day
            logger.info("AI posting system initialized")
        except Exception as e:
            logger.error(f"Error initializing AI posting system: {str(e)}")
            raise

    def should_post(self):
        """Check if we should make a new post based on timing"""
        current_time = datetime.now()
        current_date = current_time.date()

        # Don't post if we've already posted today
        if self.last_post_date == current_date:
            logger.info("Already posted today")
            return False

        # Only post at the specified hour
        if current_time.hour != self.posting_hour:
            logger.info(f"Not posting hour (current: {current_time.hour}, target: {self.posting_hour})")
            return False

        return True

    def generate_post(self):
        """Generate a new AI-focused crypto post"""
        try:
            # Get latest news and trending coins
            news = self.news_aggregator.get_latest_news()
            trending = self.news_aggregator.get_trending_ai_coins()

            if not news:
                logger.info("No new AI crypto news found")
                return None

            # Generate tweet with our meme format
            tweet = generate_tweet(news[0], trending, self.news_aggregator)
            return tweet

        except Exception as e:
            logger.error(f"Error generating post: {str(e)}")
            return None

    def make_post(self):
        """Generate and post a new tweet if conditions are met"""
        if not self.should_post():
            return None

        tweet = self.generate_post()
        if tweet:
            try:
                # Here you would add your actual posting logic
                logger.info(f"Posting tweet: {tweet}")
                
                self.last_post_date = datetime.now().date()
                return tweet
            except Exception as e:
                logger.error(f"Error posting tweet: {str(e)}")
                return None
        return None

    def run(self, continuous=True, interval=300):
        """Run the posting system either once or continuously"""
        logger.info(f"Starting AI posting system (posting at {self.posting_hour}:00 daily)")
        
        if continuous:
            while True:
                self.make_post()
                time.sleep(interval)  # Check every 5 minutes
        else:
            return self.make_post()

if __name__ == "__main__":
    # Initialize and run the posting system
    posting_system = AIPostingSystem()
    
    # Run continuously by default
    posting_system.run(continuous=True)
