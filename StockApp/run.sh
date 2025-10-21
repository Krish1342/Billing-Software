#!/bin/bash

echo "=========================================="
echo "   Jewelry Shop Management System"
echo "=========================================="
echo

echo "Starting the application..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.7+ is required, but $python_version is installed"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install streamlit pandas plotly
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install packages"
        exit 1
    fi
fi

# Change to the script directory
cd "$(dirname "$0")"

# Start the Streamlit application
echo
echo "=========================================="
echo "Application starting..."
echo "=========================================="
echo
echo "The application will open in your default browser."
echo "If it doesn't open automatically, visit:"
echo "http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application."
echo "=========================================="
echo

python3 -m streamlit run app.py

echo
echo "Application stopped."