from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
import sqlite3
import os
import uvicorn

load_dotenv()

app = FastAPI()
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

def update_content_status(content_id: int, status: str):
    """Update content status in database"""
    conn = sqlite3.connect('content.db')
    c = conn.cursor()
    c.execute('UPDATE contents SET status = ? WHERE id = ?', (status, content_id))
    conn.commit()
    conn.close()

@app.get("/action/{token}")
async def handle_action(token: str):
    try:
        # Decode and verify token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        action = payload.get('action')
        content_id = payload.get('content_id')
        
        if not action or not content_id:
            raise HTTPException(status_code=400, message="Invalid token payload")
        
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
            raise HTTPException(status_code=400, message="Invalid action")
            
    except JWTError:
        raise HTTPException(status_code=400, message="Invalid or expired token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
