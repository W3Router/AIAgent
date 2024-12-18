from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
from pydantic import BaseModel
import sqlite3
import os
import uvicorn
from social_media_automation import SocialMediaAutomation
from posting_system import TwitterPostingSystem, PostingSystem

load_dotenv()

app = FastAPI()
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
automation = SocialMediaAutomation()
twitter_system = TwitterPostingSystem()
posting_system = PostingSystem()

class ContentRequest(BaseModel):
    platform: str
    content_type: str

class WebhookRequest(BaseModel):
    content_id: str

def update_content_status(content_id: int, status: str):
    """Update content status in database"""
    conn = sqlite3.connect('content.db')
    c = conn.cursor()
    c.execute('UPDATE contents SET status = ? WHERE id = ?', (status, content_id))
    conn.commit()
    conn.close()

@app.post("/generate_content")
async def generate_content(request: ContentRequest):
    try:
        content = automation.generate_content(platform=request.platform)
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/action/{token}")
async def handle_action(token: str):
    try:
        # Decode and verify token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        action = payload.get('action')
        content_id = payload.get('content_id')
        
        if not action or not content_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")
        
        if action == 'approve':
            update_content_status(content_id, 'approved')
            return {"message": "内容已批准，将在下一个整点发布"}
        
        elif action == 'reject':
            update_content_status(content_id, 'rejected')
            return {"message": "内容已拒绝"}
        
        elif action == 'edit':
            # 返回编辑界面
            return {"message": "编辑功能即将推出"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@app.post("/webhook/approve")
async def approve_content(request: WebhookRequest):
    try:
        content_id = request.content_id
        content = twitter_system.pending_contents.get(content_id)
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
            
        # 发布推文
        if twitter_system.post_tweet(content):
            # 从待处理内容中移除
            twitter_system.pending_contents.pop(content_id)
            return {"status": "success", "message": "Content approved and posted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to post tweet")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/reject")
async def reject_content(request: WebhookRequest):
    try:
        content_id = request.content_id
        if content_id in twitter_system.pending_contents:
            twitter_system.pending_contents.pop(content_id)
        return {"status": "success", "message": "Content rejected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/edit")
async def edit_content(request: WebhookRequest):
    try:
        content_id = request.content_id
        return {"status": "success", "message": "Edit request received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/approve/{content_id}")
async def approve_content(content_id: str):
    if content_id not in posting_system.pending_contents:
        raise HTTPException(status_code=404, detail="Content not found")
    
    details = posting_system.pending_contents[content_id]
    if details['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Content is not pending")
    
    # 发布推文
    if posting_system.post_tweet(details['content']):
        details['status'] = 'approved'
        return {"message": "Content approved and posted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post tweet")

@app.get("/reject/{content_id}")
async def reject_content(content_id: str):
    if content_id not in posting_system.pending_contents:
        raise HTTPException(status_code=404, detail="Content not found")
    
    details = posting_system.pending_contents[content_id]
    if details['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Content is not pending")
    
    # 标记为已拒绝
    details['status'] = 'rejected'
    return {"message": "Content rejected successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
