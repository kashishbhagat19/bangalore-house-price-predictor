import streamlit as st
import pandas as pd
import pydeck as pdk
from utils import model, data, calculate_emi, get_recommendations, get_lat_lon
from utils import show_navigation
import requests
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

st.set_page_config(page_title="Price Predictor", layout="wide")

if "predicted_price" not in st.session_state:
    st.session_state["predicted_price"] = None
if "price_range" not in st.session_state:
    st.session_state["price_range"] = (0, 0)
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = pd.DataFrame()
if "saved_properties" not in st.session_state:
    st.session_state["saved_properties"] = []

def get_pois(lat, lon, radius=1500, poi_types=["school", "hospital", "subway_entrance"]):
    """Fetch nearby POIs from OpenStreetMap via Overpass API."""
    pois = []
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    for poi in poi_types:
        query = f"""
        [out:json];
        node
          ["amenity"="{poi}"]
          (around:{radius},{lat},{lon});
        out;
        """
        response = requests.get(overpass_url, params={"data": query})
        data = response.json()
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", poi.title())
            pois.append({"lat": element["lat"], "lon": element["lon"], "name": name, "type": poi})
    
    return pois


st.header("🔮 Predict House Price")

# Sidebar Inputs
loc = st.selectbox("📍 Location", sorted(data["location"].unique()))
sqft = st.number_input("Total Sqft", min_value=200, max_value=10000, step=50)
beds = st.number_input("Bedrooms", min_value=1, max_value=10, step=1)
bath = st.number_input("Bathrooms", min_value=1, max_value=10, step=1)
balc = st.number_input("Balconies", min_value=0, max_value=5, step=1)

# Prediction
input_df = pd.DataFrame(
    [[loc, sqft, bath, balc, beds]],
    columns=["location", "total_sqft", "bath", "balcony", "bedrooms"],
)

if st.button("🔮 Predict Price"):
    output = model.predict(input_df)
    predicted_price = output[0] * 100000
    lower, upper = round(predicted_price*0.9, 2), round(predicted_price*1.1, 2)
    st.session_state["predicted_price"] = round(predicted_price, 2)
    st.session_state["price_range"] = (lower, upper)
    st.session_state["recommendations"] = get_recommendations(loc, sqft, beds, predicted_price)

if st.session_state["predicted_price"]:
    price = st.session_state["predicted_price"]
    lower, upper = st.session_state["price_range"]

    st.subheader(f"💰 Predicted Price: ₹ {price:,.2f}")
    st.info(f"Estimated Range: ₹ {lower:,.2f} – ₹ {upper:,.2f}")

    # Recommendations
    st.subheader("🤖 Recommendations")
    recs = st.session_state["recommendations"]
    st.dataframe(recs if not recs.empty else pd.DataFrame({"Note":["No recommendations found"]}))

    # Save property
    if st.button("💾 Save this Property"):
        st.session_state["saved_properties"].append({
            "Location": loc, "Sqft": sqft, "Bedrooms": beds,
            "Bathrooms": bath, "Balconies": balc, "Predicted Price": price
        })
        st.success("Property saved ✅")

    # lat, lon = get_lat_lon(loc)
    # if lat and lon:
    #     st.subheader("📍 Location on Map")

    #     st.pydeck_chart(pdk.Deck(
    #         map_style=None,  # None = OpenStreetMap
    #         initial_view_state=pdk.ViewState(
    #             latitude=lat,
    #             longitude=lon,
    #             zoom=12
    #         ),
    #         layers=[
    #             pdk.Layer(
    #                 "ScatterplotLayer",
    #                 data=[{"lat": lat, "lon": lon}],
    #                 get_position="[lon, lat]",
    #                 get_color="[200, 30, 0, 160]",
    #                 get_radius=300,
    #             )
    #         ],
    #         tooltip={"text": "Location: ({lat}, {lon})"}
    #     ))


    def get_pois(lat, lon, radius=1500, poi_types=["school", "hospital", "subway_entrance"]):
        """Fetch nearby POIs from OpenStreetMap via Overpass API."""
        pois = []
        overpass_url = "http://overpass-api.de/api/interpreter"
    
        for poi in poi_types:
            query = f"""
            [out:json];
            node
              ["amenity"="{poi}"]
              (around:{radius},{lat},{lon});
            out;
            """
            response = requests.get(overpass_url, params={"data": query})
            data = response.json()
            for element in data.get("elements", []):
                name = element.get("tags", {}).get("name", poi.title())
                pois.append({
                    "lat": float(element["lat"]),
                    "lon": float(element["lon"]),
                    "name": name,
                    "type": poi
                })
        return pois

    lat, lon = get_lat_lon(loc)
    if lat and lon:
        st.subheader("📍 Property Location & Nearby POIs")

        # Property marker
        property_df = pd.DataFrame([{"lat": lat, "lon": lon, "name": "Property", "type": "Property"}])

        # Fetch nearby POIs
        poi_df = pd.DataFrame(get_pois(lat, lon))

        # Combine property and POIs
        map_df = pd.concat([property_df, poi_df], ignore_index=True)

        # Add color column
        map_df["color"] = map_df["type"].apply(
            lambda x: [255, 0, 0, 200] if x == "Property" else [0, 128, 255, 160]
        )

        # # Render map
        # st.pydeck_chart(pdk.Deck(
        #     map_style=None,  # OpenStreetMap
        #     initial_view_state=pdk.ViewState(
        #         latitude=lat,
        #         longitude=lon,
        #         zoom=14
        #     ),
        #     layers=[
        #         pdk.Layer(
        #             "ScatterplotLayer",
        #             data=map_df,
        #             get_position=["lon", "lat"],   # ✅ Use list of column names
        #             get_fill_color="color",        # ✅ Use precomputed color column
        #             get_radius=100,
        #             pickable=True,
        #         )
        #     ],
        #     tooltip={"html": "<b>{name}</b><br>Type: {type}", "style": {"color": "white"}}
        # ))

        # Render map with CARTO tiles (no API key required)
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",  # Dark theme
    # You can also try "light_all" for light mode:
    # map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=14
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position=["lon", "lat"],   
                    get_fill_color="color",        
                    get_radius=100,
                    pickable=True,
                )
            ],
            tooltip={"html": "<b>{name}</b><br>Type: {type}", "style": {"color": "white"}}
        ))

    