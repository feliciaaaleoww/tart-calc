# 🥧 Tart Production Calculator

A password-protected web app for managing tart production counts. Automatically syncs with Shopify to provide real-time production numbers for your bakers.

## 🌟 Features

- **🚀 Automated Sync**: Fetches orders from Shopify hourly (or on demand)
- **👁️ Single-Page Viewer**: Instant access for bakers to view counts
- **📅 Smart Dates**: Defaults to tomorrow's or day-after's production based on 12PM cutoff
- **🔒 Secure**: API keys stored locally; only aggregated counts are shared
- **🕵️ Data Verification**: View hidden order IDs to verify specific orders
- **📊 Optimized**: Handles thousands of orders with "Open Order" filtering

## 🚀 Quick Start (Local Testing)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run Home.py
   ```

3. **Manual Sync:**
   - Double-click **`Manual_Sync.command`** in your folder to trigger an instant update.

## 📦 Deployment to Streamlit Cloud

The app is deployed on Streamlit Cloud and connected to your GitHub repository.

- **Main File**: `Home.py`
- **Secrets**: Configured in Streamlit Cloud Dashboard (`admin_password`, `viewer_password`)

## 📖 How to Use

### For Admin (You):
1. **Automatic**: The system runs every hour in the background.
2. **Manual Update**: Double-click `Manual_Sync.command` on your Mac.
3. **Verify**: Open the link to check the counts.

### For Bakers:
1. Open the **App Link**
2. Enter the **Viewer Password**
3. Select the **Delivery Date**
4. View production summaries!

## 📁 File Structure

```
sharecalc/
├── Home.py                 # Single-page Viewer App
├── sync_shopify.py         # Automation script (Backend)
├── run_sync.sh             # Shell wrapper for automation
├── Manual_Sync.command     # Clickable button for manual sync
├── data/
│   └── production_data.json  # Synced data
├── .streamlit/
│   └── secrets.toml       # Passwords (Local)
└── .env                    # Shopify API Keys (Local - NEVER SHARE)
```

## 🔒 Security Notes

- ✅ **API Keys**: Stored in `.env` (gitignored, local only)
- ✅ **Customer Data**: Processed locally. Only aggregated counts are uploaded.
- ✅ **Passwords**: Stored in `.streamlit/secrets.toml` or Streamlit Cloud Secrets.
