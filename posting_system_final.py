import os
import tweepy
import logging
import time
import signal
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from real_crypto_news import CryptoNewsAggregator, generate_tweet
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure requests retry strategy
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

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure rotating log handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "logs/twitter_bot.log",
            maxBytes=1024*1024,  # 1MB
            backupCount=5  # Keep 5 backup files
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self):
        self.last_successful_operation = datetime.now()
        self.max_inactive_time = timedelta(hours=6)  # Restart after 6 hours of inactivity
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5  # Restart after 5 consecutive errors

    def update_success(self):
        self.last_successful_operation = datetime.now()
        self.consecutive_errors = 0

    def record_error(self):
        self.consecutive_errors += 1
        return self.consecutive_errors >= self.max_consecutive_errors

    def should_restart(self):
        inactive_time = datetime.now() - self.last_successful_operation
        return (inactive_time > self.max_inactive_time or 
                self.consecutive_errors >= self.max_consecutive_errors)

class AIPostingSystem:
    def __init__(self):
        """Initialize AI posting system"""
        try:
            self.health_check = HealthCheck()
            load_dotenv()
            logger.info("Environment variables loaded")
            
            # Initialize news aggregator with retry mechanism
            self.news_aggregator = CryptoNewsAggregator(http_session=http)
            logger.info("News aggregator initialized with retry mechanism")
            
            self.posting_hour = 19  # Set posting time to 19:00 (7 PM)
            self.posting_window_minutes = 5  # Post within first 5 minutes of the hour
            self.max_retries = 3
            self.retry_delay = 30  # seconds
            self.last_post_date = None
            self.initialize_twitter_api()
            logging.info(f"AI posting system initialized - Will post at {self.posting_hour:02d}:00")
            
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise

    def initialize_twitter_api(self):
        try:
            # Initialize Twitter client
            try:
                consumer_key = os.getenv('TWITTER_API_KEY')
                consumer_secret = os.getenv('TWITTER_API_SECRET')
                access_token = os.getenv('TWITTER_ACCESS_TOKEN')
                access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                
                logger.info("Initializing Twitter API...")
                logger.info(f"Using tweepy version: {tweepy.__version__}")
                
                # Check environment variables
                if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                    raise ValueError("Missing Twitter API credentials")
                
                # Initialize Twitter client with new version
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
                self.client = None
                raise
            
            self.setup_signal_handlers()
            self.health_check.update_success()
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
            raise

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful termination"""
        signal.signal(signal.SIGTERM, self.handle_termination)
        signal.signal(signal.SIGINT, self.handle_termination)

    def handle_termination(self, signum, frame):
        """Handle termination signals gracefully"""
        logger.info("Received termination signal. Cleaning up...")
        sys.exit(0)

    def restart_system(self):
        """Restart the system"""
        logger.warning("Initiating system restart...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def should_post_now(self):
        """Check if it's time to post"""
        current_time = datetime.now()
        
        # Check if already posted today
        if self.last_post_date == current_time.date():
            logger.debug("Already posted today")
            return False
        
        # Check if within posting window (within 2 minutes of target time)
        target_datetime = current_time.replace(
            hour=self.posting_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        time_diff = abs((current_time - target_datetime).total_seconds() / 60)
        should_post = time_diff <= self.posting_window_minutes  # Within 5 minutes of target time
        
        if should_post:
            logger.info(f"Posting window active - Current time: {current_time.strftime('%H:%M:%S')}")
        else:
            logger.debug(f"Outside posting window - Current time: {current_time.strftime('%H:%M:%S')}, Target: {target_datetime.strftime('%H:%M:%S')}")
        
        return should_post

    def generate_post(self):
        """Generate a new AI-focused crypto post"""
        try:
            retry_count = 0
            
            while retry_count < self.max_retries:
                try:
                    logger.info(f"Attempt {retry_count + 1}/{self.max_retries} to generate post")
                    # Get latest news and trending coins
                    news = self.news_aggregator.get_latest_news()
                    trending = self.news_aggregator.get_trending_ai_coins()

                    if news:
                        # Generate tweet with our meme format
                        tweet = generate_tweet(news[0], trending, self.news_aggregator)
                        logger.info("Successfully generated news-based content")
                        return tweet
                    else:
                        logger.warning("No new AI crypto news found")
                        retry_count += 1
                        if retry_count < self.max_retries:
                            logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                            time.sleep(self.retry_delay)
                        continue

                except ConnectionError as ce:
                    logger.warning(f"Connection error on attempt {retry_count + 1}: {str(ce)}")
                    retry_count += 1
                    if retry_count < self.max_retries:
                        logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                        time.sleep(self.retry_delay)
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {retry_count + 1}: {str(e)}")
                    retry_count += 1
                    if retry_count < self.max_retries:
                        logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                        time.sleep(self.retry_delay)
                    continue

            # If all retries failed, return None
            logger.warning("All attempts to fetch news failed")
            return None

        except Exception as e:
            logger.error(f"Critical error in generate_post: {str(e)}")
            return None

    def post_to_twitter(self, tweet_content):
        """Post tweet to Twitter"""
        try:
            if not self.client:
                raise Exception("Twitter client not initialized")
            
            response = self.client.create_tweet(text=tweet_content)
            tweet_id = response.data['id']
            logger.info(f"Successfully posted tweet (ID: {tweet_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            return False

    def make_post(self):
        """Generate and post a new tweet if conditions are met"""
        try:
            if not self.should_post_now():
                return None

            logger.info("Generating post content...")
            tweet = self.generate_post()
            if tweet:
                logger.info(f"Successfully generated tweet: {tweet}")
                logger.info("Attempting to post tweet...")
                
                if self.post_to_twitter(tweet):
                    self.last_post_date = datetime.now().date()
                    logger.info(f"Updated last post date to: {self.last_post_date}")
                    self.health_check.update_success()
                    return tweet
                else:
                    if self.health_check.record_error():
                        self.restart_system()
                    return None
            else:
                logger.error("Failed to generate content")
                if self.health_check.record_error():
                    self.restart_system()
                return None
        except Exception as e:
            logger.error(f"Error in make_post: {str(e)}")
            if self.health_check.record_error():
                self.restart_system()
            return None

    def run(self, continuous=True, interval=60):
        """Run the posting system either once or continuously"""
        logger.info(f"Starting AI posting system - Will post at {self.posting_hour:02d}:00")
        
        if continuous:
            while True:
                try:
                    self.make_post()
                    
                    # Check if restart is needed
                    if self.health_check.should_restart():
                        logger.warning("Health check triggered restart")
                        self.restart_system()
                        
                except Exception as e:
                    logger.error(f"Error in run loop: {str(e)}")
                    if self.health_check.record_error():
                        self.restart_system()
                finally:
                    time.sleep(interval)
        else:
            return self.make_post()

if __name__ == "__main__":
    try:
        # Initialize and run the posting system
        posting_system = AIPostingSystem()
        posting_system.run(continuous=True)
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        sys.exit(1)
