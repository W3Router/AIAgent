import os
import logging
from dotenv import load_dotenv
from posting_system_final import AIPostingSystem

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_post_now():
    """Test posting functionality immediately"""
    try:
        # 初始化系统
        posting_system = AIPostingSystem()
        
        # 生成推文
        tweet = posting_system.generate_post()
        if not tweet:
            logger.error("Failed to generate tweet content")
            return False
            
        logger.info(f"Generated tweet content: {tweet}")
        
        # 尝试发送推文
        try:
            if posting_system.client is None:
                logger.error("Twitter client not initialized")
                return False
                
            response = posting_system.client.create_tweet(text=tweet)
            logger.info(f"Successfully posted test tweet: {tweet}")
            print("✅ Test tweet posted successfully!")
            print(f"Tweet content: {tweet}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            print("❌ Failed to post tweet")
            print(f"Error: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print("❌ Test failed")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting post test...")
    test_post_now() 