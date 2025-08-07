#!/usr/bin/env python3
"""
Chatbot Startup Script
A simple script to launch the AI chatbot application.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = ['flask', 'flask-cors', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def start_server():
    """Start the Flask server"""
    print("🚀 Starting chatbot server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def open_browser():
    """Open the chatbot in the default browser"""
    print("🌐 Opening chatbot in your browser...")
    time.sleep(2)  # Give the server time to start
    try:
        webbrowser.open('http://localhost:5000')
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please manually open: http://localhost:5000")

def main():
    """Main function"""
    print("🤖 AI Chatbot Startup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("📦 Installing missing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        sys.exit(1)
    
    print("✅ All checks passed!")
    print()
    
    # Ask user if they want to open browser automatically
    try:
        response = input("🌐 Open browser automatically? (y/n): ").lower().strip()
        auto_open = response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    # Start server and optionally open browser
    if auto_open:
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    start_server()

if __name__ == "__main__":
    main() 