from real_crypto_news import CryptoNewsAggregator, generate_tweet
import logging
from datetime import datetime, timedelta

# Set up logging with custom date
class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Override the timestamp with our custom date
        return self.custom_date.strftime('%Y-%m-%d %H:%M:%S,%f')

    def set_custom_date(self, date):
        self.custom_date = date

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers with custom formatter
file_handler = logging.FileHandler("ai_posts.log")
stream_handler = logging.StreamHandler()
formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def generate_test_tweets(date, count=5):
    """Generate some test tweets for a specific date"""
    aggregator = CryptoNewsAggregator()
    
    # Set custom date for logging
    formatter.set_custom_date(date)
    
    # Different test news for January 22
    test_news = {
        'title': 'AI Trading Bots Achieve 89% Win Rate in Volatile Market, Traditional Traders NGMI',
        'description': 'AI-powered trading systems demonstrate unprecedented success in recent market volatility.',
        'ai_insights': [
            'AI bots adapting to market conditions in real-time',
            'Machine learning models outperforming human traders',
            'New generation of AI agents showing remarkable consistency'
        ]
    }
    
    # Generate multiple tweets with different formats
    for i in range(count):
        # Simulate different times throughout the day
        hour = 8 + (i * 3)  # Tweets at 8am, 11am, 2pm, 5pm, 8pm
        formatter.set_custom_date(date.replace(hour=hour))
        tweet = generate_tweet(test_news, [], aggregator)
        logger.info(f"Would post tweet: {tweet}")

if __name__ == "__main__":
    # Generate tweets for January 22nd
    jan_22 = datetime(2025, 1, 22, 8, 0, 0)
    generate_test_tweets(jan_22)
