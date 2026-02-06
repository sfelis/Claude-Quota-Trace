#!/bin/bash
#
# Floating Ball - Installation Script
# Sets up the Python environment and dependencies
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "  Floating Ball - Installation Script"
echo "================================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}Warning: This app is designed for macOS.${NC}"
    echo "It may not work correctly on other platforms."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        echo -e "${RED}Error: Python 3.9+ is required. Found: Python $PYTHON_VERSION${NC}"
        echo "Please install Python 3.9 or later."
        echo "  brew install python@3.11"
        exit 1
    fi
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.9+:"
    echo "  brew install python@3.11"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Python dependencies installed successfully.${NC}"
else
    echo -e "${RED}Error installing Python dependencies.${NC}"
    exit 1
fi

# Install Playwright browser
echo ""
echo "Installing Playwright Chromium browser..."
echo "(This may take a few minutes on first run)"
playwright install chromium

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Playwright browser installed successfully.${NC}"
else
    echo -e "${RED}Error installing Playwright browser.${NC}"
    exit 1
fi

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p ~/.floating-ball
echo -e "${GREEN}Data directory created at ~/.floating-ball${NC}"

# Done!
echo ""
echo "================================================"
echo -e "${GREEN}  Installation complete!${NC}"
echo "================================================"
echo ""
echo "To run the app:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start the app:"
echo "     python3 main.py"
echo ""
echo "Or use the run script:"
echo "     ./run.sh"
echo ""
echo "First time setup:"
echo "  - Right-click the ball → Settings"
echo "  - Click 'Login with Claude'"
echo "  - Complete login in the browser"
echo "  - Select your organization"
echo "  - Click Save"
echo ""
