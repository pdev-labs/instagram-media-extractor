#!/bin/bash
echo "=== Instagram Media Extractor Installer ==="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python 3 before running this script."
    exit 1
fi

echo "Python 3 is installed."

# Setup virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    echo "On Debian/Ubuntu, you might need to run: sudo apt install python3-venv"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "To run the script interactively, use:"
echo "  ./ig_media_extractor.py"
echo ""
echo "Note: The script will automatically activate its own virtual environment."
