import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from utils import data
from utils import show_navigation
import plotly.express as px

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

st.set_page_config(page_title="Bangalore Housing Insights", layout="wide")
st.header("📊 Bangalore Housing Market Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price vs Sqft (sample)")
    fig = px.scatter(
        data.sample(500),
        x="total_sqft",
        y="price_per_sqft",
        color="location",
        title="Price per Sqft vs Area",
        opacity=0.6,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Bedroom Distribution")
    fig = px.histogram(
        data,
        x="bedrooms",
        nbins=20,
        title="Bedroom Count Distribution",
        color_discrete_sequence=["indianred"],
    )
    st.plotly_chart(fig, use_container_width=True)

with st.expander("View Bangalore Housing Market Trends"):

    # 1️⃣ Average Price per Sqft by Location
    st.subheader("🏘️ Average Price per Sqft by Location")
    avg_price_per_location = data.groupby("location")["price_per_sqft"].mean().sort_values(ascending=False)
    fig1 = px.bar(
        avg_price_per_location.head(10).reset_index(),
        x="location",
        y="price_per_sqft",
        color="price_per_sqft",
        title="Top 10 Locations by Avg Price per Sqft",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Price Distribution
    st.subheader("💰 House Price Distribution")
    fig2 = px.histogram(
        data,
        x="price",
        nbins=50,
        title="Distribution of House Prices in Bangalore",
        color_discrete_sequence=["indianred"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3️⃣ Bedroom vs Price
    st.subheader("🛏️ Bedrooms vs Price")
    fig3 = px.box(
        data,
        x="bedrooms",
        y="price",
        color="bedrooms",
        title="Price vs Number of Bedrooms",
        points="all"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Correlation Heatmap (optional)
    st.subheader("📈 Feature Correlation with Price")
    corr = data[["price","total_sqft","bath","balcony","bedrooms","price_per_sqft"]].corr()
    fig4 = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Heatmap"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.success("✅ Insights generated from Cleaned Bangalore Housing Data")
