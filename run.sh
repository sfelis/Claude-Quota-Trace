#!/bin/bash
#
# Floating Ball - Run Script
# Activates venv and starts the app
#

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Please run ./install.sh first."
    exit 1
fi

# Activate and run
source venv/bin/activate
python3 main.py "$@"
