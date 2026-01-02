#!/bin/bash
# Shopify Sync Runner Script
# This script runs the Shopify sync and handles any errors

cd "$(dirname "$0")"

# Load environment variables
source .env 2>/dev/null

# Fix for git credentials in launchd (allows finding Keychain)
export HOME=/Users/rc

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the sync script using absolute python path
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 sync_shopify.py >> logs/sync.log 2>&1

# Exit with the same code as the Python script
exit $?
