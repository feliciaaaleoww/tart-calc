# 🔧 Shopify Integration Setup Guide

## 📋 Prerequisites

Before starting, you'll need:
1. Shopify Admin access
2. Python 3.7+ installed
3. Git configured on your Mac

---

## 🔥 NEW: Tag-Based Order Logic

The system now processes orders based on **tags**.
- Every order must have a tag in the format: `DD-MM-YYYY` (e.g., `02-01-2026`).
- The viewer will let bakers select a specific date to see counts for that day.
- Orders without a date tag will be grouped under "No Date Tag".
- **Default View Logic**:
  - Before 12:00 PM: Defaults to **Tomorrow's** orders.
  - After 12:00 PM: Defaults to **Day After Tomorrow's** orders.

---

## Step 1: Get Shopify API Credentials

### Create a Custom App in Shopify

1. **Go to Shopify Admin** → Settings → Apps and sales channels
2. Click **"Develop apps"** (or "Develop apps for your store")
3. Click **"Create an app"**
4. **App name**: `Tart Calculator Sync`
5. Click **"Create app"**

### Configure API Scopes

1. Click **"Configure Admin API scopes"**
2. Find and check: **`read_orders`**
3. Click **"Save"**

### Install and Get Token

1. Click **"Install app"**
2. Confirm installation
3. Click **"Reveal token once"**
4. **Copy the Admin API access token** (starts with `shpat_`)
5. **Save it somewhere safe** - you'll need it in the next step

---

## Step 2: Configure Local Environment

### Install Dependencies

```bash
cd /Users/rc/Desktop/TA/sharecalc
pip3 install -r requirements.txt
```

### Create .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   nano .env
   ```

3. Replace with your actual values:
   ```
   SHOPIFY_SHOP_URL=your-shop.myshopify.com
   SHOPIFY_ACCESS_TOKEN=shpat_your_actual_token_here
   SHOPIFY_API_VERSION=2024-01
   ```

4. Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 3: Test the Sync

Run the sync script manually to test:

```bash
python3 sync_shopify.py
```

**Expected output:**
```
🚀 Starting Shopify sync at 2024-12-30 18:45:00
============================================================
✅ Connected to Shopify: your-shop.myshopify.com
📥 Fetching orders from 7 day(s) ago...
✅ Found 15 orders
📊 Processing 45 line items from 15 orders
   Processing date group: 01-01-2026
   Processing date group: 02-01-2026
✅ Data saved to data/production_data.json
✅ Changes pushed to GitHub
============================================================
✅ Sync completed successfully!
```

---

## Step 4: Set Up Automatic Hourly Sync

### Install the LaunchAgent

```bash
# Copy the plist file to LaunchAgents directory
cp com.tartcalc.shopify.sync.plist ~/Library/LaunchAgents/

# Load the agent (starts the scheduler)
launchctl load ~/Library/LaunchAgents/com.tartcalc.shopify.sync.plist
```

### Verify It's Running

```bash
# Check if the agent is loaded
launchctl list | grep tartcalc
```

You should see: `com.tartcalc.shopify.sync`

---

## Step 5: Monitor the Sync

### Check Logs

```bash
# View sync logs
tail -f logs/sync.log

# View error logs (if any)
tail -f logs/launchd.error.log
```

### Manual Trigger

You can manually trigger a sync anytime:

```bash
python3 sync_shopify.py
```

Or:

```bash
./run_sync.sh
```

---

## 🔧 Management Commands

### Stop Automatic Sync

```bash
launchctl unload ~/Library/LaunchAgents/com.tartcalc.shopify.sync.plist
```

### Start Automatic Sync

```bash
launchctl load ~/Library/LaunchAgents/com.tartcalc.shopify.sync.plist
```

### Change Sync Frequency

Edit `com.tartcalc.shopify.sync.plist` and change `StartInterval`:
- `3600` = Every hour (default)
- `1800` = Every 30 minutes
- `7200` = Every 2 hours

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.tartcalc.shopify.sync.plist
launchctl load ~/Library/LaunchAgents/com.tartcalc.shopify.sync.plist
```

---

## 🔒 Security Checklist

- ✅ `.env` file is in `.gitignore` (API credentials protected)
- ✅ `data/` folder is in `.gitignore` (raw data not committed)
- ✅ Only `production_data.json` is committed to GitHub
- ✅ Shopify API token has minimal permissions (`read_orders` only)

---

## 🆘 Troubleshooting

### Sync not running automatically

1. Check if LaunchAgent is loaded:
   ```bash
   launchctl list | grep tartcalc
   ```

2. Check error logs:
   ```bash
   cat logs/launchd.error.log
   ```

3. Make sure your Mac is awake (not sleeping)

### "Permission denied" error

```bash
chmod +x run_sync.sh
```
