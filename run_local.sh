#!/bin/bash

echo "🎯 WhatsApp Bulk Message - Local Development"
echo "============================================"
echo

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo "Please install Python and try again"
    exit 1
fi

# Make the script executable
chmod +x run_local.py

# Run the local development setup
python run_local.py
