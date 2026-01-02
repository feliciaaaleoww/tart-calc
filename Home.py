import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Tart Production Calculator", page_icon="🥧", layout="wide")

# ------------------------ PASSWORD PROTECTION ------------------------
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["viewer_password"] == st.secrets.get("viewer_password", "baker2025"):
            st.session_state["viewer_password_correct"] = True
            del st.session_state["viewer_password"]  # Don't store password
        else:
            st.session_state["viewer_password_correct"] = False

    if "viewer_password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔒 Viewer Password", type="password", on_change=password_entered, key="viewer_password"
        )
        st.info("Enter the viewer password to see tart production counts.")
        return False
    elif not st.session_state["viewer_password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "🔒 Viewer Password", type="password", on_change=password_entered, key="viewer_password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

import time

# ------------------------ MAIN VIEWER INTERFACE ------------------------
st.title("👁️ Tart Production Counts (Live V2)")

# Logout button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state["viewer_password_correct"] = False
        st.rerun()

st.markdown("---")

# Refresh button
if st.button("🔄 Refresh Data", type="primary"):
    st.rerun()

# ------------------------ LOAD DATA ------------------------
data_file = "data/production_data.json"
# Add cache buster to URL to prevent stale data
github_raw_url = f"https://raw.githubusercontent.com/rachelcyx-14/tart-calc/main/data/production_data.json?t={int(time.time())}"
data = None
source = "Unknown"

# 1. Try fetching from GitHub (Live Update)
try:
    response = requests.get(github_raw_url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        source = "☁️ GitHub (Live)"
    else:
        st.warning(f"⚠️ GitHub fetch failed (Status: {response.status_code}). Using local cache.")
except Exception as e:
    st.warning(f"⚠️ GitHub fetch error: {e}. Using local cache.")

# 2. Fallback to Local File (if GitHub fails or no internet)
if not data:
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        source = "📂 Local Cache"
    else:
        st.warning("⚠️ No production data available yet. Please ask admin to upload orders or run sync first.")
        st.stop()
    
    last_updated = data.get("last_updated", "Unknown")
    last_updated = data.get("last_updated", "Unknown")
    st.info(f"📅 **Last Synced:** {last_updated} | **Source:** {source}")
    
    try:
        # ------------------------ DATE SELECTION ------------------------
        all_datasets = data.get("datasets", {})
        
        # Fallback for old data format
        if not all_datasets and "production_summary" in data:
            all_datasets = {"Legacy / Manual Upload": data}
    
        if not all_datasets:
            st.warning("No date-tagged data found.")
            st.stop()
            
        # Get available dates and sort them
        available_dates = sorted(list(all_datasets.keys()))
        
        # Determine Default Date Logic
        # Logic:
        # - If time < 12PM: Default to Tomorrow
        # - If time >= 12PM: Default to Day After Tomorrow
        now = datetime.now()
        if now.hour < 12:
            target_date = now + timedelta(days=1)
        else:
            target_date = now + timedelta(days=2)
            
        default_date_str = target_date.strftime("%d-%m-%Y")
        
        # Find matching index for default date
        default_index = 0
        if default_date_str in available_dates:
            default_index = available_dates.index(default_date_str)
        elif "No Date Tag" in available_dates:
             # Optionally default to "No Date Tag" if target not found? Or just first available
             pass
    
        selected_date = st.selectbox(
            "📅 **Select Delivery Date**", 
            options=available_dates,
            index=default_index
        )
        
        # Get data for selected date
        selected_data = all_datasets.get(selected_date, {})
        
        if not selected_data:
            st.warning(f"No data found for {selected_date}")
            st.stop()
    
        st.markdown(f"### Showing counts for: **{selected_date}**")
        st.markdown("---")
    
        # Display data in columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Production Summary
            st.subheader("🍓 Production Summary")
            if selected_data.get("production_summary"):
                production_df = pd.DataFrame(selected_data["production_summary"])
                st.dataframe(production_df, use_container_width=True, hide_index=True)
            else:
                st.info("No production data available.")
            
            # Box Summary
            st.subheader("📦 Box Summary")
            if selected_data.get("box_summary"):
                box_df = pd.DataFrame(selected_data["box_summary"])
                st.dataframe(box_df, use_container_width=True, hide_index=True)
            else:
                st.info("No box data available.")
        
        with col2:
            # Total Summary
            st.subheader("📊 Total Summary")
            if selected_data.get("total_summary"):
                total_df = pd.DataFrame(selected_data["total_summary"])
                st.dataframe(total_df, use_container_width=True, hide_index=True)
            else:
                st.info("No total summary available.")
            
            # Party Set Summary
            if selected_data.get("party_summary") and len(selected_data["party_summary"]) > 0:
                st.subheader("🎉 Party Set Summary")
                party_df = pd.DataFrame(selected_data["party_summary"])
                st.dataframe(party_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please contact admin if this problem persists.")

st.markdown("---")
# Hidden Order IDs Section
with st.expander("🕵️ Show Included Order IDs"):
    if selected_data.get("order_ids"):
        st.write(", ".join(selected_data["order_ids"]))
        st.caption(f"Total Orders: {len(selected_data['order_ids'])}")
    else:
        st.info("No order IDs available for this date.")

st.caption("💡 Data updates automatically every hour. Click 'Refresh Data' to pull the latest update.")
