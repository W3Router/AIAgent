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

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 设置日志轮转
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "logs/twitter_bot.log",
            maxBytes=1024*1024,  # 1MB
            backupCount=5  # 保留5个备份文件
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self):
        self.last_successful_operation = datetime.now()
        self.max_inactive_time = timedelta(hours=6)  # 6小时无活动则重启
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5  # 连续5次错误则重启

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
            
            # 初始化带有重试机制的新闻聚合器
            self.news_aggregator = CryptoNewsAggregator(http_session=http)
            logger.info("News aggregator initialized with retry mechanism")
            
            self.posting_hour = 19  # 设置固定发送时间为19:00
            self.posting_minute = 0
            self.last_post_date = None
            
            # 初始化 Twitter 客户端
            try:
                consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
                consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
                access_token = os.getenv('TWITTER_ACCESS_TOKEN')
                access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                
                logger.info("Initializing Twitter API...")
                logger.info(f"Using tweepy version: {tweepy.__version__}")
                
                # 检查环境变量
                if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                    raise ValueError("Missing Twitter API credentials")
                
                # 初始化新版本的 Twitter 客户端
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
            logger.info(f"AI posting system initialized - Will post daily at {self.posting_hour:02d}:{self.posting_minute:02d}")
            self.health_check.update_success()
            
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise

    def setup_signal_handlers(self):
        """设置信号处理器以优雅地处理终止信号"""
        signal.signal(signal.SIGTERM, self.handle_termination)
        signal.signal(signal.SIGINT, self.handle_termination)

    def handle_termination(self, signum, frame):
        """优雅地处理终止信号"""
        logger.info("Received termination signal. Cleaning up...")
        sys.exit(0)

    def restart_system(self):
        """重启系统"""
        logger.warning("Initiating system restart...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def should_post_now(self):
        """检查是否应该发送推文"""
        current_time = datetime.now()
        
        # 检查是否已经在今天发送过
        if self.last_post_date == current_time.date():
            logger.debug("Already posted today")
            return False
        
        # 检查是否在发送时间窗口内（19:00-19:05）
        should_post = (current_time.hour == self.posting_hour and 
                      0 <= current_time.minute < 5)
        
        if should_post:
            logger.info(f"Posting window active - Current time: {current_time.strftime('%H:%M:%S')}")
        else:
            logger.debug(f"Outside posting window - Current time: {current_time.strftime('%H:%M:%S')}")
        
        return should_post

    def post_to_twitter(self, tweet_content):
        """发送推文到 Twitter"""
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
        logger.info(f"Starting AI posting system - Will post daily at {self.posting_hour:02d}:{self.posting_minute:02d}")
        
        if continuous:
            while True:
                try:
                    self.make_post()
                    
                    # 检查是否需要重启
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
        # 初始化并运行发帖系统
        posting_system = AIPostingSystem()
        posting_system.run(continuous=True)
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        sys.exit(1)
