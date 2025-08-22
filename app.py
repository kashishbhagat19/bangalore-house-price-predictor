import streamlit as st
from utils import model, data, calculate_emi, get_recommendations, get_lat_lon 
import hashlib
import json  
from utils import login_form


# Hide default Streamlit pages menu in sidebar
hide_pages_style = """
    <style>
    div[data-testid="stSidebarNav"] {display: none;}
    div[data-testid="stSidebarNavItems"] {display: none;}
    div[data-testid="stSidebarNavSeparator"] {display: none;}
    </style>
"""
st.markdown(hide_pages_style, unsafe_allow_html=True)

# Show login if not logged in
if not st.session_state.get("logged_in", False):
    login_form()
    st.stop()

# ----------------- Sidebar -----------------
st.sidebar.success(f"Logged in as: {st.session_state['username']}")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.switch_page("app.py") 


# ------------------- Page Config -------------------
st.set_page_config(
    page_title="🏠 Bangalore House Price Predictor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------- Sidebar Navigation -------------------
st.sidebar.title("🔎 Navigation")

st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_predict.py", label="🔮 Predict Price")
st.sidebar.page_link("pages/2_property_tools.py", label="🏦 Financial Tools")
st.sidebar.page_link("pages/3_market_insights.py", label="📊 Market Insights")
st.sidebar.page_link("pages/4_history.py", label="🧾 History")
st.sidebar.page_link("pages/5_compare.py", label="📌 Compare Properties")

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")

# ------------------- Home Page Content -------------------
st.title("🏠 Bangalore House Price Predictor Dashboard")
st.write(
    """
    Welcome to the **Bangalore House Price Predictor**!  
    Use the sidebar to navigate:
    - 🔮 **Predict Price**: Get house price predictions with recommendations.
    - 📊 **Market Insights**: Explore Bangalore real estate trends.
    - 🧾 **History**: Review and download your prediction history.
    - 📌 **Compare Properties**: Compare saved properties side by side.
    """
)

# Quick stats
st.subheader("📈 Dataset Overview")
st.write(f"Total Records: {len(data):,}")
st.dataframe(data.head(10), use_container_width=True)

st.success("✅ Use the sidebar to start exploring predictions and insights!")
