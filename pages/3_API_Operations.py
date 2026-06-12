import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="API Operations", layout="wide")
st.title("API Operations")

API_URL = "https://hotel-booking-analysis-1.onrender.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}

st.header("1. Submit a New Booking (POST)")

with st.form("booking_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        hotel = st.selectbox("Hotel Type", ["City Hotel", "Resort Hotel"])
        lead_time = st.number_input("Lead Time (Days)", min_value=0, value=15)
        special_requests = st.number_input(
            "Special Requests", min_value=0, max_value=5, value=0
        )

    with col2:
        weekend_nights = st.number_input("Weekend Nights", min_value=0, value=1)
        week_nights = st.number_input("Week Nights", min_value=0, value=2)

    with col3:
        adults = st.number_input("Adults", min_value=1, value=2)
        children = st.number_input("Children", min_value=0, value=0)
        babies = st.number_input("Babies", min_value=0, value=0)

    submitted = st.form_submit_button("Submit Booking to API")

    if submitted:
        payload = {
            "hotel": hotel,
            "is_canceled": 0,
            "lead_time": lead_time,
            "stays_in_weekend_nights": weekend_nights,
            "stays_in_week_nights": week_nights,
            "adults": adults,
            "children": float(children),
            "babies": babies,
            "adr": 120.0,
            "total_of_special_requests": special_requests,
        }

        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            if response.status_code == 200:
                st.success("Successfully added new booking!")
            else:
                st.error(f"Failed to submit. Status code: {response.status_code}")
        except Exception:
            st.error("Could not connect to the API.")

st.divider()

st.header("2. View Recent Bookings (GET)")

col_a, col_b = st.columns([1, 4])
with col_a:
    fetch_limit = st.number_input(
        "Number of records", min_value=1, max_value=50, value=5
    )
    fetch_button = st.button("Fetch Records")

if fetch_button:
    try:
        response = requests.get(f"{API_URL}?limit={fetch_limit}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data:
                df_api = pd.DataFrame(data)
                display_cols = [
                    "hotel",
                    "lead_time",
                    "stays_in_weekend_nights",
                    "stays_in_week_nights",
                    "adults",
                    "children",
                    "total_of_special_requests",
                ]
                available_cols = [col for col in display_cols if col in df_api.columns]
                st.dataframe(
                    df_api[available_cols] if available_cols else df_api,
                    use_container_width=True,
                )
            else:
                st.warning("No records found.")
        else:
            st.error("Failed to fetch data from the API.")
    except Exception:
        st.error("Could not connect to the API.")
