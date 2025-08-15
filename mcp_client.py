# mcp_client.py
import socket
import json

class MCPClient:
    def __init__(self, host='127.0.0.1', port=8002):
        self.host = host
        self.port = port

    def send_request(self, task, prompt, system_prompt=None, platform=None):
        try:
            request = {
                "task": task,
                "prompt": prompt
            }
            
            if system_prompt:
                request["system_prompt"] = system_prompt
            if platform:
                request["platform"] = platform

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(json.dumps(request).encode('utf-8'))
                response = s.recv(4096).decode('utf-8')
                return json.loads(response)
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Example usage
if __name__ == "__main__":
    client = MCPClient()
    
    # QA Example
    response = client.send_request(
        task="qa",
        prompt="What is the capital of France?",
        system_prompt="You are a helpful assistant"
    )
    print("QA Response:", response)
    
    # Image Generation Example
    response = client.send_request(
        task="image_generation",
        prompt="A beautiful sunset over mountains"
    )
    print("Image Generation Response:", response)
    
    # Platform Content Example
    response = client.send_request(
        task="platform_content",
        prompt="Announcing our new AI product",
        platform="twitter"
    )
    print("Platform Content Response:", response)