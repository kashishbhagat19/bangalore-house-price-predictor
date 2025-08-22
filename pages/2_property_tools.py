import streamlit as st
from utils import calculate_emi
from utils import show_navigation
from utils import login_form

hide_pages_style = """
    <style>
    div[data-testid="stSidebarNav"] {display: none;}
    div[data-testid="stSidebarNavItems"] {display: none;}
    div[data-testid="stSidebarNavSeparator"] {display: none;}
    </style>
"""
st.markdown(hide_pages_style, unsafe_allow_html=True)

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

st.set_page_config(page_title="Property Tools", layout="wide")

st.header("🏦 Property Financial Tools")

predicted_price = st.session_state.get("predicted_price", None)

if predicted_price:
    st.write(f"Using Predicted Price: ₹ {predicted_price:,.2f}")

    # ---------------- EMI Calculator ----------------
    st.subheader("🏦 Loan EMI Calculator")
    loan = st.number_input("Loan Amount (₹)", value=int(predicted_price), step=50000)
    rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=20.0, value=7.5, step=0.1)
    years = st.number_input("Tenure (Years)", min_value=1, max_value=30, value=20, step=1)

    if st.button("📉 Calculate EMI"):
        emi = calculate_emi(loan, rate, years)
        st.session_state['emi'] = emi
        st.success(f"💸 EMI: ₹ {emi:,.2f}/month")

    # ---------------- Rental Yield Calculator ----------------
    st.subheader("🏠 Rental Yield Calculator")
    purchase_price = st.number_input(
        "Enter Property Price (₹)", 
        min_value=100000.0, 
        step=50000.0, 
        value=float(predicted_price)
    )

    estimated_monthly_rent = (purchase_price * 0.03) / 12  # 3% annually
    monthly_rent = st.number_input(
        "Expected Monthly Rent (₹)", 
        min_value=1000.0, 
        step=500.0, 
        value=float(estimated_monthly_rent)
    )

    if monthly_rent > 0 and purchase_price > 0:
        annual_rent = monthly_rent * 12
        rental_yield = (annual_rent / purchase_price) * 100

        st.metric(label="Annual Rent", value=f"₹{annual_rent:,.0f}")
        st.metric(label="Rental Yield", value=f"{rental_yield:.2f}%")

        if rental_yield < 3:
            st.warning("⚠️ Low yield. This property may not be great for investment.")
        elif 3 <= rental_yield < 5:
            st.info("ℹ️ Average yield. Decent investment potential.")
        else:
            st.success("✅ High yield! Strong investment.")

    # ---------------- Affordability Check ----------------
    st.subheader("💵 Affordability Check")
    monthly_income = st.number_input("Enter your Monthly Income (₹)", min_value=0, step=5000)
    emi_to_check = st.session_state.get('emi', calculate_emi(purchase_price, rate, years))

    if st.button("🔍 Check Affordability"):
        max_affordable_emi = monthly_income * 0.35  # 35% of income rule
        st.write(f"💰 Max Affordable EMI (35% of income): ₹{max_affordable_emi:,.2f}")
        st.write(f"💸 Estimated EMI: ₹{emi_to_check:,.2f}")

        if emi_to_check <= max_affordable_emi:
            st.success("✅ You can afford this property!")
        else:
            st.error("❌ This property may be too expensive for your income.")

else:
    st.info("No predicted price found. Please run the Predict Price page first.")