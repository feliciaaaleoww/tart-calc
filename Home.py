import streamlit as st

st.set_page_config(
    page_title="Tart Production Calculator",
    page_icon="🥧",
    layout="wide"
)

st.title("🥧 Tart Production Calculator")

st.markdown("""
Welcome to the Tart Production Calculator!

### 👤 Admin
Upload order CSV files and process production summaries.

### 👁️ Viewer
View the latest tart production counts (for bakers).

---

**Please select a page from the sidebar to continue.**
""")

st.info("💡 **Tip**: Use the sidebar on the left to navigate between Admin and Viewer pages.")
