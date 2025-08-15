# backend.py
from pydantic import BaseModel
from typing import List, Optional, Literal
from fastapi import FastAPI
import uvicorn

# Create FastAPI app first to avoid circular imports
app = FastAPI(
    title="Softvance AI Agent", 
    description="AI Agent with multiple capabilities", 
    version="0.2.0"
)
from fastapi.middleware.cors import CORSMiddleware

# Add this after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import AI functions after app is created
from ai_agent import ask_ai, generate_image, generate_platform_content

class Message(BaseModel):
    role: str  # "human" or "ai"
    content: str

class AIRequest(BaseModel):
    task: Literal["qa", "image_generation", "platform_content"]
    prompt: str
    system_prompt: Optional[str] = None
    chat_history: Optional[List[Message]] = None
    platform: Optional[str] = None

@app.post("/ai-task")
def ai_task_endpoint(request: AIRequest):
    """Single endpoint for all AI tasks"""
    try:
        if request.task == "qa":
            if not request.prompt:
                return {"error": "Prompt is required for Q&A task"}
                
            response = ask_ai(
                question=request.prompt,
                system_prompt=request.system_prompt,
                chat_history=request.chat_history
            )
            
            if response["status"] == "error":
                return {"error": response["output"], "status": "error"}
                
            return {
                "response": response["output"],
                "task": "qa",
                "status": "success"
            }
            
        elif request.task == "image_generation":
            if not request.prompt:
                return {"error": "Prompt is required for image generation"}
                
            response = generate_image(request.prompt)
            if response["status"] == "error":
                return {"error": response["error"], "status": "error"}
                
            return {
                "image": response["image"],
                "prompt": response["prompt"],
                "task": "image_generation",
                "status": "success"
            }
            
        elif request.task == "platform_content":
            if not request.prompt:
                return {"error": "Prompt is required for content generation"}
            if not request.platform:
                return {"error": "Platform is required for content generation"}
                
            response = generate_platform_content(request.prompt, request.platform)
            if response["status"] == "error":
                return {"error": response["error"], "status": "error"}
                
            return {
                "content": response["content"],
                "platform": response["platform"],
                "task": "platform_content",
                "status": "success"
            }
            
        else:
            return {"error": "Invalid task type", "status": "error"}
            
    except Exception as e:
        return {
            "error": f"Error processing your request: {str(e)}",
            "status": "error"
        }


# Replace the __main__ block in backend.py with:
if __name__ == "__main__":
    import os
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8006)),
        timeout_keep_alive=20
    )