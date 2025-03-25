#!/bin/bash
# Preload script for VAPI Tools
# This script preloads the Python environment to make the Raycast command run faster

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
echo "Preloading VAPI Tools environment..."
echo "Script directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment and check/install dependencies
echo "Activating virtual environment and checking dependencies..."
source "$SCRIPT_DIR/venv/bin/activate"
if ! pip list | grep -q vapi; then
    echo "Installing VAPI SDK..."
    pip install vapi_server_sdk
else
    echo "VAPI SDK already installed."
fi

echo "Environment is ready! Raycast commands should now run quickly."
echo "You can close this terminal window."