import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import pickle as pk
import streamlit as st
import hashlib
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_navigation():
    st.sidebar.markdown("## 🔍 Navigation")
    st.sidebar.page_link("app.py", label="🏠 Home")
    st.sidebar.page_link("pages/1_predict.py", label="🔮 Predict Price")
    st.sidebar.page_link("pages/2_property_tools.py", label="🏦 Financial Tools")
    st.sidebar.page_link("pages/3_market_insights.py", label="📊 Market Insights")
    st.sidebar.page_link("pages/4_history.py", label="🧾 History")
    st.sidebar.page_link("pages/5_compare.py", label="📌 Compare Properties")


# Load model & dataset once
with open("models/house_prediction_model.pkl", "rb") as f:
    model = pk.load(f)
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


@st.cache_resource
def connect_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1is5qnnFOvdK00M7niiLtawjhXM_fMiS4GCwQtxUyNs8").sheet1

    expected_headers = [
        "User", "Location", "Sqft", "Bedrooms", "Bathrooms", "Balconies", "Predicted Price"
    ]
    existing = sheet.row_values(1)
    if existing != expected_headers:
        sheet.clear()
        sheet.append_row(expected_headers)

    return sheet

sheet = connect_gsheet()

def save_prediction(user, loc, sqft, beds, bath, balc, price):
    sheet = connect_gsheet()
    sheet.append_row([user, loc, sqft, beds, bath, balc, price])

def load_predictions(user):
    """Load only the logged-in user's predictions"""
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if not df.empty and "User" in df.columns:
        df = df[df["User"] == user]  # filter only this user
    return df

def clear_user_history(user):
    sheet = connect_gsheet()
    records = sheet.get_all_records()

    # Keep only rows that are NOT from this user
    filtered_records = [r for r in records if r["User"] != user]

    # Clear everything
    sheet.clear()

    # Write header back
    sheet.append_row(["User", "Location", "Sqft", "Bedrooms", "Bathrooms", "Balconies", "Predicted Price"])

    # Write back only rows from other users
    for row in filtered_records:
        sheet.append_row([
            row["User"], row["Location"], row["Sqft"], row["Bedrooms"],
            row["Bathrooms"], row["Balconies"], row["Predicted Price"]
        ])

def load_history(user):
    sheet = connect_gsheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        return df

    # Filter only this user's rows
    return df[df["User"] == user]

def connect_gsheet_tab(tab_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client.open_by_key("1Bj53zxVKeLE_jVTTITq8xokIsj8JO4klbdJbwj0z4O4").worksheet(tab_name)

# ---------------- Saved Properties ----------------
def save_property_for_user(user, loc, sqft, beds, bath, balc, price):
    sheet = connect_gsheet_tab("SavedProperties")
    sheet.append_row([user, loc, sqft, beds, bath, balc, price])

def load_saved_properties(user):
    sheet = connect_gsheet_tab("SavedProperties")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        return []

    # Only this user’s saved properties
    df = df[df["User"] == user]
    return df.to_dict(orient="records")

def clear_saved_properties(user):
    sheet = connect_gsheet_tab("SavedProperties")
    records = sheet.get_all_records()

    # Keep rows from other users
    filtered_records = [r for r in records if r["User"] != user]

    # Clear everything
    sheet.clear()
    sheet.append_row(["User", "Location", "Sqft", "Bedrooms", "Bathrooms", "Balconies", "Predicted Price"])

    # Re-add data from other users
    for row in filtered_records:
        sheet.append_row([
            row["User"], row["Location"], row["Sqft"], row["Bedrooms"],
            row["Bathrooms"], row["Balconies"], row["Predicted Price"]
        ])
