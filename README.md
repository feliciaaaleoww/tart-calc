# 🥧 Tart Production Calculator

A password-protected web app for managing tart production counts. Upload order CSVs and share production summaries with your bakers.

## 🌟 Features

- **👤 Admin Page**: Password-protected CSV upload and processing
- **👁️ Viewer Page**: Password-protected display for bakers to view tart counts
- **🔒 Secure**: Two-tier password system (admin + viewer)
- **📊 Real-time Updates**: Bakers can refresh to see latest counts
- **📱 Mobile-Friendly**: Works on phones and tablets

## 🚀 Quick Start (Local Testing)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run Home.py
   ```

3. **Access the app:**
   - Open your browser to `http://localhost:8501`
   - Configure passwords in `.streamlit/secrets.toml` before first use

## 📦 Deployment to Streamlit Cloud (FREE)

### Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   cd /Users/rc/Desktop/TA/sharecalc
   git init
   ```

2. **Add all files:**
   ```bash
   git add .
   ```

3. **Commit:**
   ```bash
   git commit -m "Initial commit - Tart calculator app"
   ```

4. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it `tart-calculator` (or any name you prefer)
   - Choose **Private** (recommended for security)
   - Click "Create repository"

5. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/tart-calculator.git
   git branch -M main
   git push -u origin main
   ```
   
   Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy your app:**
   - Click "New app"
   - Select your repository: `tart-calculator`
   - Main file path: `Home.py`
   - Click "Deploy"

3. **Configure Secrets (IMPORTANT):**
   - In Streamlit Cloud dashboard, go to your app settings
   - Click "Secrets"
   - Add the following:
     ```toml
     admin_password = "YOUR_STRONG_ADMIN_PASSWORD"
     viewer_password = "YOUR_BAKER_PASSWORD"
     ```
   - Replace with your own passwords
   - Click "Save"

4. **Get your URL:**
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
   - Share the viewer page with bakers: `https://YOUR_APP_NAME.streamlit.app/Viewer`

## 🔑 Password Configuration

### Local Development
Edit `.streamlit/secrets.toml` to change passwords locally.

### Production (Streamlit Cloud)
Change passwords in the Streamlit Cloud dashboard under "Secrets".

## 📖 How to Use

### For Admin (You):
1. Go to the **Admin** page
2. Enter admin password
3. Upload your order CSV files
4. Click "Process Orders & Save"
5. Data is now available for bakers to view

### For Bakers:
1. Go to the **Viewer** page (or share direct link)
2. Enter viewer password
3. View production counts
4. Click "Refresh Data" to see latest updates

## 📁 File Structure

```
sharecalc/
├── Home.py                 # Landing page
├── pages/
│   ├── 1_👤_Admin.py      # Admin upload page
│   └── 2_👁️_Viewer.py     # Viewer display page
├── data/
│   └── production_data.json  # Saved production data (auto-created)
├── .streamlit/
│   └── secrets.toml       # Password configuration (local only)
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔒 Security Notes

- ✅ CSV files are **never stored** on the server
- ✅ Only production summaries are saved (no customer data)
- ✅ Passwords are stored securely in Streamlit secrets
- ✅ `.gitignore` prevents secrets from being committed to GitHub

## 🆘 Troubleshooting

**Q: Bakers see "No production data available"**
- A: Admin needs to upload CSV files first through the Admin page

**Q: Password not working**
- A: Check that secrets are configured correctly in Streamlit Cloud dashboard

**Q: App not updating after CSV upload**
- A: Bakers need to click "Refresh Data" button on Viewer page

## 📞 Support

For issues or questions, contact the admin.
