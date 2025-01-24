import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def test_twitter_post():
    try:
        # 加载环境变量
        load_dotenv()
        logger.info("环境变量已加载")
        
        # 检查 Twitter 凭证是否存在
        credentials = {
            'TWITTER_CONSUMER_KEY': os.getenv('TWITTER_CONSUMER_KEY'),
            'TWITTER_CONSUMER_SECRET': os.getenv('TWITTER_CONSUMER_SECRET'),
            'TWITTER_ACCESS_TOKEN': os.getenv('TWITTER_ACCESS_TOKEN'),
            'TWITTER_ACCESS_TOKEN_SECRET': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        }
        
        missing_credentials = [k for k, v in credentials.items() if not v]
        if missing_credentials:
            logger.error(f"缺少以下 Twitter 凭证: {', '.join(missing_credentials)}")
            return False
            
        logger.info("正在初始化 Twitter API...")
        # 初始化 Twitter API v2 客户端
        client = setup_twitter_client()
        logger.info("Twitter API 初始化成功")
        
        # 发送测试推文
        test_tweet = "这是一条测试推文 " + "测试时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"准备发送推文: {test_tweet}")
        
        response = client.create_tweet(text=test_tweet)
        
        print("✅ 推文发送成功！")
        print(f"推文内容: {test_tweet}")
        print(f"推文 ID: {response.data['id']}")
        return True
        
    except Exception as e:
        logger.error(f"发送推文失败: {str(e)}", exc_info=True)
        print("❌ 发送推文失败")
        print(f"错误信息: {str(e)}")
        return False

if __name__ == "__main__":
    test_twitter_post() 