# import streamlit as st
# import pandas as pd

# st.set_page_config(page_title="Saved & Compare", page_icon="📌")

# st.title("📌 Saved & Compare Properties")

# if "saved_properties" not in st.session_state:
#     st.session_state["saved_properties"] = []

# if st.session_state["saved_properties"]:
#     saved = st.session_state["saved_properties"]

#     # Show properties as card-style grid
#     for i in range(0, len(saved), 2):
#         cols = st.columns(2)
#         for j, col in enumerate(cols):
#             if i + j < len(saved):
#                 prop = saved[i + j]
#                 with col:
#                     st.markdown(
#                         f"""
#                         <div style="background-color:#f9f9f9; padding:20px; border-radius:15px; 
#                                     box-shadow:0px 2px 8px rgba(0,0,0,0.1); margin-bottom:20px;">
#                             <h4 style="margin:0; color:#2c3e50;">🏡 {prop['Location']}</h4>
#                             <p><b>Sqft:</b> {prop['Sqft']}</p>
#                             <p><b>Bedrooms:</b> {prop['Bedrooms']} | 
#                                <b>Bathrooms:</b> {prop['Bathrooms']} | 
#                                <b>Balconies:</b> {prop['Balconies']}</p>
#                             <p style="font-size:18px; color:#27ae60;">
#                                <b>Predicted Price:</b> ₹ {prop['Predicted Price']:,}</p>
#                         </div>
#                         """,
#                         unsafe_allow_html=True
#                     )

#     # Clear all saved properties
#     if st.button("🗑️ Clear Saved Properties"):
#         st.session_state["saved_properties"] = []
#         st.success("Saved properties cleared!")

# else:
#     st.caption("No properties saved yet. Go to the main page and save some houses for comparison.")


import streamlit as st
import pandas as pd
from utils import show_navigation

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

st.header("📌 Compare Saved Properties")

if "saved_properties" not in st.session_state:
    st.session_state["saved_properties"] = []

saved = st.session_state["saved_properties"]

if saved:
    df = pd.DataFrame(saved)
    st.dataframe(df, use_container_width=True)

    # Side-by-side comparison
    st.subheader("🔍 Side by Side Comparison")
    for i, prop in enumerate(saved):
        with st.expander(f"Property {i+1}"):
            st.write(f"📍 Location: {prop['Location']}")
            st.write(f"📏 Sqft: {prop['Sqft']}")
            st.write(f"🛏 Bedrooms: {prop['Bedrooms']}")
            st.write(f"🛁 Bathrooms: {prop['Bathrooms']}")
            st.write(f"🏡 Balconies: {prop['Balconies']}")
            st.write(f"💰 Predicted Price: ₹ {prop['Predicted Price']:,.2f}")

    # Clear comparison
    if st.button("🗑 Clear Saved Properties"):
        st.session_state["saved_properties"] = []
        st.success("Cleared all saved properties ✅")
else:
    st.info("No properties saved yet. Go to 🔮 Predict Price and save some!")
