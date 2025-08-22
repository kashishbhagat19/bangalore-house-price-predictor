import streamlit as st
import pandas as pd
import os
from utils import show_navigation


hide_pages_style = """
    <style>
    div[data-testid="stSidebarNav"] {display: none;}
    div[data-testid="stSidebarNavItems"] {display: none;}
    div[data-testid="stSidebarNavSeparator"] {display: none;}
    </style>
"""
st.markdown(hide_pages_style, unsafe_allow_html=True)

show_navigation()

from utils import login_form

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Show login if not logged in
if not st.session_state["logged_in"]:
    login_form()
    st.stop()  # stops execution until user logs in

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")

st.set_page_config(page_title="Prediction History", layout="wide")

st.header("🧾 Prediction History")

HISTORY_FILE = "D:\House-Price-Prediction\prediction_history.csv"

# Load history
if os.path.exists(HISTORY_FILE):
    history_df = pd.read_csv(HISTORY_FILE)
else:
    history_df = pd.DataFrame(columns=[
        "Location", "Sqft", "Bedrooms", "Bathrooms", "Balconies", "Predicted Price"
    ])

# Show table
if not history_df.empty:
    st.dataframe(history_df, use_container_width=True)

    # Download
    csv = history_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download History", csv, "prediction_history.csv", "text/csv")

    # Clear
    if st.button("🗑 Clear History"):
        history_df = pd.DataFrame(columns=history_df.columns)
        history_df.to_csv(HISTORY_FILE, index=False)
        st.success("History cleared ✅")

else:
    st.info("No history available yet. Make predictions to see them here!")
