from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from social_media_automation import SocialMediaAutomation

app = FastAPI()
automation = SocialMediaAutomation()

class ContentRequest(BaseModel):
    platform: str = "twitter"
    content_type: str = "tips"
    topic: Optional[str] = None
    
class ContentWithImageRequest(BaseModel):
    platform: str = "twitter"
    content_type: str = "tips"
    topic: Optional[str] = None
    style: Optional[str] = "digital art"

@app.post("/generate_content")
async def generate_content(request: ContentRequest):
    content = automation.generate_content(
        platform=request.platform,
        content_type=request.content_type,
        topic=request.topic
    )
    
    if content is None:
        return {"status": "success", "content": None}
        
    return {"status": "success", "content": content}

@app.post("/generate_content_with_image")
async def generate_content_with_image(request: ContentWithImageRequest):
    result = await automation.generate_content_with_image(
        platform=request.platform,
        content_type=request.content_type,
        topic=request.topic,
        style=request.style
    )
    
    if result is None:
        return {"status": "error", "message": "Failed to generate content and image"}
        
    return {
        "status": "success",
        "content": result['content'],
        "image_url": result['image'],
        "image_prompt": result['image_prompt']
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
