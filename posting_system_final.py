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
            logger.info("环境变量加载完成")
            
            self.news_aggregator = CryptoNewsAggregator()
            logger.info("新闻聚合器初始化完成")
            
            self.last_post_date = None
            self.posting_hour = 22  # 晚上10点
            self.posting_minute = 30  # 30分
            
            # 初始化 Twitter 客户端
            try:
                consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
                consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
                access_token = os.getenv('TWITTER_ACCESS_TOKEN')
                access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                
                logger.info("正在初始化 Twitter API...")
                logger.info(f"使用的 tweepy 版本: {tweepy.__version__}")
                logger.info("检查环境变量:")
                logger.info(f"consumer_key 存在: {'是' if consumer_key else '否'}")
                logger.info(f"consumer_secret 存在: {'是' if consumer_secret else '否'}")
                logger.info(f"access_token 存在: {'是' if access_token else '否'}")
                logger.info(f"access_token_secret 存在: {'是' if access_token_secret else '否'}")
                
                # 使用基本参数初始化客户端
                self.client = tweepy.Client(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )
                logger.info("Twitter API 初始化成功")
            except Exception as e:
                logger.error(f"Twitter API 初始化失败: {str(e)}")
                logger.error(f"错误类型: {type(e).__name__}")
                logger.error(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详情'}")
                self.client = None
            
            logger.info("AI 发推系统初始化完成")
        except Exception as e:
            logger.error(f"系统初始化失败: {str(e)}")
            raise

    def should_post(self):
        """检查是否应该发送推文"""
        current_time = datetime.now()
        current_date = current_time.date()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # 检查是否是指定的发送时间
        if current_hour != self.posting_hour or current_minute != self.posting_minute:
            return False
        
        # 检查今天是否已经发送过
        if self.last_post_date == current_date:
            logger.info(f"今天已经发送过推文了 (上次发送时间: {self.last_post_date})")
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
        
        # Schedule posts for 10:30 PM daily
        schedule.every().day.at("22:30").do(posting_system.make_post)
        
        # Display next run time
        next_run = schedule.next_run()
        logger.info(f"System started, scheduled to post at 22:30 daily")
        logger.info(f"Next post scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"System started, scheduled to post at 22:30 daily")
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
