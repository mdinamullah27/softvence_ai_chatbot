# mcp_server.py
import socket
import json
from threading import Thread
import uvicorn
from ai_agent import ask_ai, generate_image, generate_platform_content

class MCPServer:
    def __init__(self, host='127.0.0.1', port=8004):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"MCP Server listening on {self.host}:{self.port}")

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                request = json.loads(data)
                response = self.process_request(request)
                client_socket.send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            client_socket.send(json.dumps({"status": "error", "error": str(e)}).encode('utf-8'))
        finally:
            client_socket.close()

    def process_request(self, request):
        try:
            task = request.get('task')
            
            if task == 'qa':
                result = ask_ai(
                    question=request.get('prompt'),
                    system_prompt=request.get('system_prompt'),
                    chat_history=request.get('chat_history')
                )
                return {
                    "response": result["output"],
                    "status": "success"
                }
                
            elif task == 'image_generation':
                result = generate_image(request.get('prompt'))
                return {
                    "image": result["image"],
                    "status": "success"
                }
                
            elif task == 'platform_content':
                result = generate_platform_content(
                    request.get('prompt'),
                    request.get('platform')
                )
                return {
                    "content": result["content"],
                    "status": "success"
                }
                
            else:
                return {"status": "error", "error": "Invalid task"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_thread = Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()

def run_servers():
    # Import inside function to avoid circular imports
    from backend import app
    
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=8003),
        daemon=True
    )
    fastapi_thread.start()
    
    # Start MCP server in main thread
    mcp_server = MCPServer()
    mcp_server.start()

if __name__ == "__main__":
    run_servers()