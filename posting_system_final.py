import os
import json
import logging
import time
import signal
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pathlib import Path
from real_crypto_news import CryptoNewsAggregator, generate_tweet

# 设置日志轮转
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            "twitter_bot.log",
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
            self.news_aggregator = CryptoNewsAggregator()
            self.posting_hour = 19  # 设置固定发送时间为19:00
            self.posting_minute = 0
            self.last_post_date = None
            self.setup_signal_handlers()
            
            logger.info(f"AI posting system initialized - Will post daily at {self.posting_hour:02d}:{self.posting_minute:02d}")
            self.health_check.update_success()
        except Exception as e:
            logger.error(f"Error initializing AI posting system: {str(e)}")
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
        
        return should_post

    def generate_post(self):
        """Generate a new AI-focused crypto post"""
        try:
            max_retries = 3
            retry_count = 0
            retry_delay = 30  # 30秒的重试延迟
            
            while retry_count < max_retries:
                try:
                    logger.info(f"Attempt {retry_count + 1}/{max_retries} to generate post")
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
                        if retry_count < max_retries:
                            logger.info(f"Waiting {retry_delay} seconds before retry...")
                            time.sleep(retry_delay)
                        continue

                except ConnectionError as ce:
                    logger.warning(f"Connection error on attempt {retry_count + 1}: {str(ce)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {retry_count + 1}: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    continue

            # 如果所有重试都失败了，使用默认内容
            logger.warning("All attempts to fetch news failed, using default content")
            return self.generate_default_post()

        except Exception as e:
            logger.error(f"Critical error in generate_post: {str(e)}")
            return self.generate_default_post()

    def make_post(self):
        """Generate and post a new tweet if conditions are met"""
        try:
            current_time = datetime.now()
            
            # 检查是否已经在今天发送过
            if self.last_post_date == current_time.date():
                logger.debug("Already posted today")
                return None
            
            # 检查是否在发送时间窗口内（19:00-19:05）
            should_post = (current_time.hour == self.posting_hour and 
                         0 <= current_time.minute < 5)
            
            if not should_post:
                logger.debug(f"Outside posting window - Current time: {current_time.strftime('%H:%M:%S')}")
                return None
                
            logger.info(f"Posting window active - Current time: {current_time.strftime('%H:%M:%S')}")
            logger.info("Generating post content...")
            tweet = self.generate_post()
            
            if tweet:
                logger.info(f"Successfully generated tweet: {tweet}")
                logger.info("Attempting to post tweet...")
                self.last_post_date = current_time.date()
                logger.info(f"Updated last post date to: {self.last_post_date}")
                self.health_check.update_success()
                return tweet
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
