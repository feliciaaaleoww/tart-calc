#!/bin/bash
# Move to the script directory
cd "$(dirname "$0")"

# Run the sync
echo "🥧 Starting Manual Sync..."
./run_sync.sh

# Keep window open to show status
echo "---------------------------------------"
if [ $? -eq 0 ]; then
    echo "✅ Sync Completed! You can close this window."
else
    echo "❌ Sync Failed. Check logs above."
fi
echo "---------------------------------------"
read -p "Press Enter to close..."
