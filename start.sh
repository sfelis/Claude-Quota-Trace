#!/bin/bash
# Launch floating ball app detached from terminal

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Please run ./install.sh first."
    exit 1
fi

# Kill any existing instances
pkill -f "python.*main.py" 2>/dev/null

# Activate venv and start in background
source venv/bin/activate
nohup python3 main.py > /dev/null 2>&1 &

echo "Floating ball started (PID: $!)"
echo "To stop: ./stop.sh"
