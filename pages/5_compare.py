import streamlit as st
import pandas as pd
from utils import show_navigation
from utils import load_saved_properties, clear_saved_properties
from utils import login_form

hide_pages_style = """
    <style>
    div[data-testid="stSidebarNav"] {display: none;}
    div[data-testid="stSidebarNavItems"] {display: none;}
    div[data-testid="stSidebarNavSeparator"] {display: none;}
    </style>
"""
st.markdown(hide_pages_style, unsafe_allow_html=True)

st.set_page_config(page_title="Comparison", layout="wide")

show_navigation()

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

st.header("📌 Compare Saved Properties")

username = st.session_state["username"]
saved = load_saved_properties(username)

if saved:
    df = pd.DataFrame(saved)
    st.dataframe(df, use_container_width=True)

    st.subheader("🔍 Side by Side Comparison")
    for i, prop in enumerate(saved):
        with st.expander(f"Property {i+1}"):
            st.write(f"📍 Location: {prop['Location']}")
            st.write(f"📏 Sqft: {prop['Sqft']}")
            st.write(f"🛏 Bedrooms: {prop['Bedrooms']}")
            st.write(f"🛁 Bathrooms: {prop['Bathrooms']}")
            st.write(f"🏡 Balconies: {prop['Balconies']}")
            st.write(f"💰 Predicted Price: ₹ {prop['Predicted Price']:,.2f}")

    if st.button("🗑 Clear My Saved Properties"):
        clear_saved_properties(username)
        st.success("Your saved properties were cleared ✅")
        st.rerun()
else:
    st.info("No properties saved yet. Go to 🔮 Predict Price and save some!")
