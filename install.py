#!/usr/bin/env python3
"""
Installer script for the Smart File Sorter application.
This script provides a simple way to install the application for users
who may not be familiar with Python packaging.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current Python version: {sys.version}")
        return False
    return True

def check_pip():
    """Check if pip is installed."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: pip is not installed or not working properly.")
        print("Please install pip and try again.")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "groq", "python-dotenv", "customtkinter"],
                      check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def install_application():
    """Install the application using pip."""
    print("Installing Smart File Sorter...")
    try:
        # Get the directory of this script
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Install the package in development mode
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(script_dir)],
                      check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error installing application: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut for the application."""
    try:
        # Get user's home directory
        home_dir = Path.home()
        desktop_dir = home_dir / "Desktop"
        
        if not desktop_dir.exists():
            print("Desktop directory not found. Skipping shortcut creation.")
            return False
        
        # Create shortcut based on platform
        if sys.platform == "win32":
            # Windows shortcut
            shortcut_path = desktop_dir / "Smart File Sorter.bat"
            with open(shortcut_path, "w") as f:
                f.write("@echo off\n")
                f.write("start \"\" \"" + sys.executable + "\" -m file_sorter_app.main\n")
        else:
            # Linux/Mac shortcut
            shortcut_path = desktop_dir / "Smart File Sorter"
            with open(shortcut_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"{sys.executable} -m file_sorter_app.main\n")
            os.chmod(shortcut_path, 0o755)
        
        print(f"Desktop shortcut created at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False

def setup_env_file():
    """Set up the .env file with the Groq API key."""
    # Get the directory of this script
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    env_example = script_dir / ".env.example"
    env_file = script_dir / ".env"
    
    # Check if .env already exists
    if env_file.exists():
        print(".env file already exists. Skipping creation.")
        return True
    
    # Copy .env.example to .env if it exists
    if env_example.exists():
        shutil.copy(env_example, env_file)
    else:
        # Create .env file
        with open(env_file, "w") as f:
            f.write("# Groq API Key for Smart File Sorter\n")
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
    
    # Ask user for API key
    print("\nTo use the Smart File Sorter, you need a Groq API key.")
    api_key = input("Enter your Groq API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file with the provided API key
        with open(env_file, "r") as f:
            content = f.read()
        
        content = content.replace("your_groq_api_key_here", api_key)
        
        with open(env_file, "w") as f:
            f.write(content)
        
        print("API key saved to .env file.")
    else:
        print("No API key provided. You can add it later to the .env file.")
    
    return True

def main():
    """Main installer function."""
    print("=== Smart File Sorter Installer ===\n")
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Install application
    if not install_application():
        return 1
    
    # Set up .env file
    setup_env_file()
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\n=== Installation Complete ===")
    print("You can now run the Smart File Sorter by typing 'file-sorter' in your terminal")
    print("or by using the desktop shortcut if it was created.")
    print("\nEnjoy organizing your files!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
