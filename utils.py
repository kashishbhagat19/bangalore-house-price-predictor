import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import pickle as pk
import streamlit as st
import hashlib
import json

def show_navigation():
    st.sidebar.markdown("## 🔍 Navigation")
    st.sidebar.page_link("app.py", label="🏠 Home")
    st.sidebar.page_link("pages/1_predict.py", label="🔮 Predict Price")
    st.sidebar.page_link("pages/2_property_tools.py", label="🏦 Financial Tools")
    st.sidebar.page_link("pages/3_market_insights.py", label="📊 Market Insights")
    st.sidebar.page_link("pages/4_history.py", label="🧾 History")
    st.sidebar.page_link("pages/5_compare.py", label="📌 Compare Properties")


# Load model & dataset once
model = pk.load(open("house_prediction_model.pkl", "rb"))
data = pd.read_csv("Cleaned_data.csv")
data["price_per_sqft"] = (data["price"] * 100000) / data["total_sqft"]

def calculate_emi(principal, annual_rate, tenure_years):
    """Calculate EMI for loan"""
    r = annual_rate / (12 * 100)
    n = tenure_years * 12
    emi = (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return round(emi, 2)

def get_recommendations(location, sqft, bedrooms, price, top_n=5):
    df = data[data["location"] != location]
    df_similar = df[
        (df["bedrooms"].between(bedrooms - 1, bedrooms + 1)) &
        (df["total_sqft"].between(sqft - 200, sqft + 200))
    ]
    df_similar["price_per_sqft_diff"] = abs(df_similar["price_per_sqft"] - (price/sqft))
    recommendations = df_similar.sort_values("price_per_sqft_diff").head(top_n)
    return recommendations[["location", "total_sqft", "bedrooms", "price"]]

def get_lat_lon(location_name: str):
    """Fetch latitude & longitude for a location"""
    try:
        geolocator = Nominatim(user_agent="house_price_app")
        loc = geolocator.geocode(f"{location_name}, Bangalore, India")
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        return None, None
    return None, None

USER_DB = "users.json"

# ---------------- User DB Helpers ----------------
def load_users():
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    users = load_users()["users"]
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

 # ---------------- Login Form ----------------
def login_form():
    st.header("🔑 Login / Register")
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        register_button = st.form_submit_button("Register")

        if login_button:
            if authenticate(username_input, password_input):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_input
                st.success(f"Welcome, {username_input}!")
                st.switch_page("app.py")  # reload page to show home/dashboard
            else:
                st.error("Invalid username or password")

        if register_button:
            users = load_users()
            if username_input in users["users"]:
                st.error("Username already exists")
            else:
                users["users"][username_input] = {
                    "password": hash_password(password_input),
                    "saved_properties": []
                }
                save_users(users)
                st.success("User registered successfully! You can now login.")

# if not st.session_state["logged_in"]:
#     st.markdown(
#         """
#         <style>
#         .login-box {
#             max-width: 350px;
#             margin: auto;
#             padding: 2rem;
#             border: 1px solid #ddd;
#             border-radius: 12px;
#             background-color: #f9f9f9;
#             box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     with st.container():
#         st.markdown('<div class="login-box">', unsafe_allow_html=True)
#         st.title("🔑 Login")

#         choice = st.radio("Select", ["Login", "Register"], horizontal=True)

#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")

#         if choice == "Login":
#             if st.button("Login"):
#                 if authenticate(username, password):
#                     st.session_state["logged_in"] = True
#                     st.session_state["username"] = username
#                     st.switch_page("app.py")  # redirect to home
#                 else:
#                     st.error("❌ Invalid username or password")
#         else:
#             if st.button("Register"):
#                 users = load_users()
#                 if username in users["users"]:
#                     st.error("⚠️ Username already exists")
#                 else:
#                     users["users"][username] = {"password": hash_password(password)}
#                     save_users(users)
#                     st.success("✅ Registered successfully! Please login.")

#         st.markdown('</div>', unsafe_allow_html=True)