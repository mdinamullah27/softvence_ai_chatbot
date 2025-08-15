# softvence_ai_chatbot
LIVE LINK: https://softvence-ai-chatbot.onrender.com/
# Softvance AI Agent

## Features
- Q&A with web search
- Image generation
- Platform-specific content creation
- MCP integration

## Installation
1. Clone repo
2. Create .env with API keys
3. `pip install -r requirements.txt`
4. Run `python mcp_server.py` for backend
5. Run `streamlit run frontend.py` for UI

## API Keys Needed
- GROQ_API_KEY
- TAVILY_API_KEY
- STABILITY_API_KEY
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant AgentCore
    participant Tools
    
    User->>Frontend: Submit Prompt (Q/Image/Content)
    Frontend->>Backend: POST /ai-task {task_type, prompt}
    Backend->>AgentCore: Route Request
    alt Q&A
        AgentCore->>Tools: Tavily Search (if needed)
        Tools-->>AgentCore: Web Results
    else Image Gen
        AgentCore->>Tools: Stability API Call
    else Content
        AgentCore->>Tools: LLM Platform Template
    end
    AgentCore-->>Backend: Formatted Response
    Backend-->>Frontend: JSON Response
    Frontend->>User: Display Result
