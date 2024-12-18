from flask import Flask, jsonify, redirect
import logging
from posting_system import TwitterPostingSystem
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("review_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
posting_system = TwitterPostingSystem()

@app.route('/')
def home():
    return "EON Protocol Review Server"

@app.route('/api/review/approve/<content_id>')
def approve_content(content_id):
    try:
        # 在这里实现审核逻辑
        logger.info(f"Content {content_id} approved")
        
        # 发送推文
        content = posting_system.pending_contents.get(content_id)
        if content:
            if posting_system.post_tweet(content):
                logger.info(f"Successfully posted content {content_id}")
                # 从待处理内容中移除
                posting_system.pending_contents.pop(content_id)
                return redirect("/api/review/success")
            else:
                logger.error(f"Failed to post content {content_id}")
                return redirect("/api/review/error")
        else:
            logger.error(f"Content {content_id} not found")
            return redirect("/api/review/error")
            
    except Exception as e:
        logger.error(f"Error approving content {content_id}: {e}")
        return redirect("/api/review/error")

@app.route('/api/review/reject/<content_id>')
def reject_content(content_id):
    try:
        logger.info(f"Content {content_id} rejected")
        # 从待处理内容中移除
        if content_id in posting_system.pending_contents:
            posting_system.pending_contents.pop(content_id)
        return redirect("/api/review/success")
    except Exception as e:
        logger.error(f"Error rejecting content {content_id}: {e}")
        return redirect("/api/review/error")

@app.route('/api/review/edit/<content_id>')
def edit_content(content_id):
    try:
        logger.info(f"Content {content_id} needs editing")
        return redirect("/api/review/success")
    except Exception as e:
        logger.error(f"Error marking content {content_id} for edit: {e}")
        return redirect("/api/review/error")

@app.route('/api/review/success')
def success():
    return """
    <html>
        <body style="text-align: center; padding-top: 50px; font-family: Arial, sans-serif;">
            <h1 style="color: #28a745;">✅ Action Completed Successfully</h1>
            <p>You can close this window now.</p>
        </body>
    </html>
    """

@app.route('/api/review/error')
def error():
    return """
    <html>
        <body style="text-align: center; padding-top: 50px; font-family: Arial, sans-serif;">
            <h1 style="color: #dc3545;">❌ Error</h1>
            <p>Something went wrong. Please try again or contact support.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # 获取端口，默认为5000
    port = int(os.getenv("REVIEW_SERVER_PORT", "5000"))
    app.run(host='0.0.0.0', port=port)
