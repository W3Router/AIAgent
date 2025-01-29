import os
import logging
from dotenv import load_dotenv
from posting_system_final import AIPostingSystem
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_post_now():
    """Test posting functionality immediately"""
    try:
        logger.info("开始测试发推功能...")
        
        # 初始化系统
        posting_system = AIPostingSystem()
        
        # 检查是否应该发送
        logger.info("检查是否应该发送推文...")
        if not posting_system.should_post():
            logger.info("现在不是发送时间或今天已经发送过")
            return False
            
        # 生成推文
        logger.info("正在生成推文内容...")
        tweet = posting_system.generate_post()
        if not tweet:
            logger.error("生成推文内容失败")
            return False
            
        logger.info(f"生成的推文内容:\n{tweet}")
        
        # 尝试发送推文
        try:
            if posting_system.client is None:
                logger.error("Twitter 客户端未初始化")
                return False
                
            logger.info("正在发送推文...")
            response = posting_system.client.create_tweet(text=tweet)
            logger.info(f"推文发送成功！")
            print("\n✅ 测试推文发送成功！")
            print(f"推文内容:\n{tweet}")
            
            # 更新最后发送时间
            posting_system.last_post_date = datetime.now().date()
            logger.info(f"更新最后发送时间为: {posting_system.last_post_date}")
            
            return True
            
        except Exception as e:
            logger.error(f"发送推文失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            print("\n❌ 发送推文失败")
            print(f"错误: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        print("\n❌ 测试失败")
        print(f"错误: {str(e)}")
        return False

def test_post_twice():
    """测试连续发送两次，验证重复发送检查"""
    print("\n=== 第一次发送测试 ===")
    first_result = test_post_now()
    
    if first_result:
        print("\n=== 第二次发送测试（应该被阻止） ===")
        second_result = test_post_now()
        if not second_result:
            print("\n✅ 重复发送检查正常工作")
        else:
            print("\n❌ 重复发送检查失败")
    
if __name__ == "__main__":
    print("\n开始发推测试...\n")
    test_post_twice() 