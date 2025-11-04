#!/usr/bin/env python3
"""
Startup script for the TestFoundry Web UI
"""

import sys
import uvicorn
from pathlib import Path

# Add the web_ui directory to Python path
web_ui_path = Path(__file__).parent / "web_ui"
sys.path.insert(0, str(web_ui_path))

def main():
    """Run the FastAPI web server"""
    print("Starting TestFoundry Web UI...")
    print("Server will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "api.server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(web_ui_path)],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()