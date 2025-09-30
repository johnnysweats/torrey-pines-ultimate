#!/bin/bash

echo "Setting up golf waitlist script..."

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "Python 3 found: $(python3 --version)"
else
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
echo "Note: If you get permission errors, the script will create a virtual environment instead."
python3 -m pip install --user -r requirements.txt || {
    echo "Creating virtual environment as fallback..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo ""
    echo "Virtual environment created! To run the script:"
    echo "source venv/bin/activate && python waitlist.py"
    echo ""
    echo "To run with caffeinate:"
    echo "caffeinate -i bash -c 'source venv/bin/activate && python waitlist.py'"
}

echo ""
echo "Setup complete! To run the script:"
echo "python3 waitlist.py"
echo ""
echo "To run with caffeinate (prevents sleep):"
echo "caffeinate -i python3 waitlist.py" 