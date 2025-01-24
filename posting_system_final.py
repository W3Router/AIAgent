import os
import tweepy
import logging
from datetime import datetime
import schedule
import time
from dotenv import load_dotenv
from real_crypto_news import CryptoNewsAggregator, generate_tweet

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
            self.news_aggregator = CryptoNewsAggregator()
            self.last_post_date = None
            self.posting_hour = 12  # Post at 12 PM every day
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
                client = setup_twitter_client()
                response = client.create_tweet(text=tweet)
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

def setup_twitter_client():
    """初始化 Twitter API v2 客户端"""
    consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return client

def main():
    try:
        # Initialize and run the posting system
        posting_system = AIPostingSystem()
        
        # Set up schedule to post at 12 PM every day
        schedule.every().day.at("12:00").do(posting_system.make_post)
        
        logger.info("系统已启动，将在每天中午12:00发送推文...")
        print("系统已启动，将在每天中午12:00发送推文...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"运行时错误: {str(e)}")
                time.sleep(60)  # 发生错误后等待一分钟再继续
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
