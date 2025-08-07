#!/bin/bash

# AI Chatbot Launcher Script
echo "🤖 AI Chatbot Launcher"
echo "======================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory."
    exit 1
fi

echo "✅ All checks passed!"
echo "🚀 Starting chatbot server..."
echo "📍 Server will be available at: http://localhost:8080"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 app.py 