#!/bin/bash

# Torrey Pines Waitlist Automation Launcher
# Double-click this file to run the waitlist automation

echo "🏌️  Torrey Pines Waitlist Automation"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then: source venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
if ! python3 -c "import selenium" 2>/dev/null; then
    echo "❌ Selenium not found! Installing dependencies..."
    pip3 install selenium pytz
fi

# Run the launcher
echo "🚀 Starting waitlist automation..."
echo "💡 Tip: Choose option 3 (caffeinate) to prevent sleep during automation!"
echo ""
python3 run_waitlist.py

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo "❌ An error occurred. Press Enter to exit..."
    read
fi 