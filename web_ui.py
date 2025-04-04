#!/usr/bin/env python3
"""
Main entry point for the Web UI version of the Smart File Sorter application.
"""

import os
import sys
from src.web_app import run_web_app

if __name__ == "__main__":
    # Ensure the Groq API key is set
    if not os.getenv("GROQ_API_KEY"):
        # Try to load from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # If still not set, check if it's in the command line arguments
        if len(sys.argv) > 1 and sys.argv[1].startswith("gsk_"):
            os.environ["GROQ_API_KEY"] = sys.argv[1]
        
        # If still not set, warn the user
        if not os.getenv("GROQ_API_KEY"):
            print("Warning: GROQ_API_KEY environment variable is not set.")
            print("The application may not function correctly without a valid API key.")
            print("You can set it by creating a .env file with GROQ_API_KEY=your_key")
            print("or by passing it as the first command line argument.")
    
    # Run the web application
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    print(f"Starting Smart File Sorter Web UI on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    run_web_app(host=host, port=port, debug=debug)
