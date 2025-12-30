import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Viewer - Tart Counts", page_icon="👁️", layout="wide")

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

# ------------------------ MAIN VIEWER INTERFACE ------------------------
st.title("👁️ Tart Production Counts")

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

if not os.path.exists(data_file):
    st.warning("⚠️ No production data available yet. Please ask admin to upload orders first.")
    st.stop()

try:
    with open(data_file, "r") as f:
        data = json.load(f)
    
    last_updated = data.get("last_updated", "Unknown")
    st.info(f"📅 **Last Updated:** {last_updated}")
    
    # Display data in columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Production Summary
        st.subheader("🍓 Production Summary")
        if data.get("production_summary"):
            import pandas as pd
            production_df = pd.DataFrame(data["production_summary"])
            st.dataframe(production_df, use_container_width=True, hide_index=True)
        else:
            st.info("No production data available.")
        
        # Box Summary
        st.subheader("📦 Box Summary")
        if data.get("box_summary"):
            box_df = pd.DataFrame(data["box_summary"])
            st.dataframe(box_df, use_container_width=True, hide_index=True)
        else:
            st.info("No box data available.")
    
    with col2:
        # Total Summary
        st.subheader("📊 Total Summary")
        if data.get("total_summary"):
            total_df = pd.DataFrame(data["total_summary"])
            st.dataframe(total_df, use_container_width=True, hide_index=True)
        else:
            st.info("No total summary available.")
        
        # Party Set Summary
        if data.get("party_summary") and len(data["party_summary"]) > 0:
            st.subheader("🎉 Party Set Summary")
            party_df = pd.DataFrame(data["party_summary"])
            st.dataframe(party_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please contact admin if this problem persists.")

st.markdown("---")
st.caption("💡 Click 'Refresh Data' to see the latest updates from admin.")
