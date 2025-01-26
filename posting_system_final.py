import os
import tweepy
import logging
from datetime import datetime
import schedule
import time
from dotenv import load_dotenv
from real_crypto_news import CryptoNewsAggregator, generate_tweet
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置 requests 的重试策略
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Disable SSL warnings
urllib3.disable_warnings()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("logs/ai_posts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIPostingSystem:
    def __init__(self):
        """Initialize AI posting system"""
        try:
            load_dotenv()
            logger.info("Environment variables loaded")
            
            self.news_aggregator = CryptoNewsAggregator(http_session=http)
            logger.info("News aggregator initialized")
            
            self.last_post_date = None
            self.posting_hour = 19  # 7:00 PM
            self.posting_minute = 0  # 00 minutes
            
            # Initialize Twitter client
            try:
                consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
                consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
                access_token = os.getenv('TWITTER_ACCESS_TOKEN')
                access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                
                logger.info("Initializing Twitter API...")
                logger.info(f"Using tweepy version: {tweepy.__version__}")
                logger.info("Checking environment variables:")
                logger.info(f"consumer_key exists: {'yes' if consumer_key else 'no'}")
                logger.info(f"consumer_secret exists: {'yes' if consumer_secret else 'no'}")
                logger.info(f"access_token exists: {'yes' if access_token else 'no'}")
                logger.info(f"access_token_secret exists: {'yes' if access_token_secret else 'no'}")
                
                # Initialize client with basic parameters
                self.client = tweepy.Client(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
                self.client = None
            
            logger.info("AI posting system initialization complete")
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise

    def should_post(self):
        """Check if it's time to post"""
        current_time = datetime.now()
        current_date = current_time.date()
        
        # Only check if we've already posted today
        if self.last_post_date == current_date:
            logger.info(f"Already posted today (last post: {self.last_post_date})")
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
            max_retries = 3
            attempt_count = 0
            
            while attempt_count < max_retries:
                try:
                    if self.client is None:
                        logger.error("Twitter client not initialized")
                        attempt_count += 1
                        continue
                        
                    response = self.client.create_tweet(text=tweet)
                    logger.info(f"Successfully posted tweet: {tweet}")
                    
                    self.last_post_date = datetime.now().date()
                    return tweet
                    
                except Exception as e:
                    attempt_count += 1
                    logger.error(f"Failed to post tweet (attempt {attempt_count}): {str(e)}")
                    
                    if attempt_count < max_retries:
                        wait_time = 60 * attempt_count
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        logger.error("Maximum retry attempts reached, posting failed")
                        return None
        return None

def main():
    try:
        # Initialize and run the posting system
        posting_system = AIPostingSystem()
        
        # Get posting time
        post_time = f"{posting_system.posting_hour:02d}:{posting_system.posting_minute:02d}"
        
        # Schedule posts
        schedule.every().day.at(post_time).do(posting_system.make_post)
        
        # Display next run time
        next_run = schedule.next_run()
        logger.info(f"System started, scheduled to post daily at {post_time}")
        logger.info(f"Next post scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"System started, scheduled to post daily at {post_time}")
        print(f"Next post scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Runtime error: {str(e)}")
                time.sleep(60)
    except Exception as e:
        logger.error(f"System startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
