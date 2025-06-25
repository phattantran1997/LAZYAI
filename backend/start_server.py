import subprocess
import webbrowser
import time
import os

def start_server():
    # Start uvicorn server
    server_process = subprocess.Popen([
        "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"
    ])
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Open docs in browser
    webbrowser.open("http://127.0.0.1:8000/docs")
    
    try:
        # Keep the server running
        server_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server_process.terminate()

if __name__ == "__main__":
    start_server() 