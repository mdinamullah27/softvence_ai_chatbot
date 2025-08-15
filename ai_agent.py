# ai_agent.py
from dotenv import load_dotenv
load_dotenv()
import os
import base64
from io import BytesIO
from PIL import Image
import requests
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
STABILITY_API_KEY = os.environ.get('STABILITY_API_KEY')

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage

# Initialize LLM
llm = ChatGroq(
    temperature=0.3,
    model_name="llama3-70b-8192",
    groq_api_key=GROQ_API_KEY
)

# Initialize Tavily search
tavily = TavilySearchResults(api_key=TAVILY_API_KEY)

# Create the search tool
search_tool = Tool(
    name="tavily_search",
    func=tavily.invoke,
    description="Search the web for current information when needed"
)

# Define the default system prompt
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to web search.
Use the search tool for:
1. Current events (after 2023)
2. Fact verification
3. Breaking news
4. Recent scientific breakthroughs"""

def create_agent_executor(system_prompt=None):
    """Create a new agent executor with the given system prompt"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt or DEFAULT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    agent = create_tool_calling_agent(
        llm=llm,
        tools=[search_tool],
        prompt=prompt
    )
    
    return AgentExecutor(
        agent=agent,
        tools=[search_tool],
        verbose=True,
        handle_parsing_errors=True
    )

def ask_ai(question, system_prompt=None, chat_history=None):
    """Process a question through the AI agent"""
    try:
        executor = create_agent_executor(system_prompt)
        
        input_data = {"input": question}
        
        if chat_history:
            formatted_history = []
            for msg in chat_history:
                if isinstance(msg, dict):
                    if msg["role"] == "human":
                        formatted_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "ai":
                        formatted_history.append(AIMessage(content=msg["content"]))
                else:
                    formatted_history.append(AIMessage(content=str(msg)))
            input_data["chat_history"] = formatted_history
        
        response = executor.invoke(input_data)
        
        return {
            "output": response.get("output", "I couldn't find an answer to that."),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "output": f"Error processing your request: {str(e)}",
            "status": "error",
            "error": str(e)
        }

def generate_image(prompt):
    """Generate an image using Stability AI"""
    try:
        engine_id = "stable-diffusion-xl-1024-v1-0"
        api_host = "https://api.stability.ai"
        
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {STABILITY_API_KEY}"
            },
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            },
        )
        
        if response.status_code != 200:
            return {"status": "error", "error": f"API Error: {response.text}"}
            
        data = response.json()
        image_data = data["artifacts"][0]["base64"]
        
        return {
            "status": "success",
            "image": image_data,
            "prompt": prompt
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def generate_platform_content(prompt, platform):
    """Generate content tailored for a specific platform"""
    try:
        platform_prompts = {
            "twitter": "Create a concise tweet (280 characters max) about: {prompt}",
            "facebook": "Create a Facebook post (2-3 paragraphs) about: {prompt}",
            "linkedin": "Create a professional LinkedIn post (3-4 paragraphs) about: {prompt}"
        }
        
        if platform not in platform_prompts:
            return {"status": "error", "error": "Unsupported platform"}
            
        tailored_prompt = platform_prompts[platform].format(prompt=prompt)
        
        response = llm.invoke(tailored_prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "status": "success",
            "content": content,
            "platform": platform
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}