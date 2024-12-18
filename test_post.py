from posting_system import TwitterPostingSystem
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # 初始化系统
        posting_system = TwitterPostingSystem()
        
        # 生成内容
        content_type = posting_system.get_current_content_type()
        content = posting_system.generate_content(content_type)
        
        # 发送审核邮件
        posting_system.send_email_for_approval(content_type, content)
        logger.info(f"Sent approval email for content type: {content_type}")
        
    except Exception as e:
        logger.error(f"Error in test post: {e}")
        raise

if __name__ == "__main__":
    main()
