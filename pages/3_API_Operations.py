import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="API Operations", layout="wide")

st.title("Step 5: REST API Interaction (FastAPI)")
st.markdown("""
This page implements direct communication with the FastAPI backend deployed on Render. 
You can test GET requests with filtering and pagination, as well as submit POST requests to add new records to the dataset.
""")

API_URL = "https://hotel-booking-analysis-1.onrender.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}

st.divider()

st.header("1. Retrieve Data (GET Request)")

col_get1, col_get2, col_get3 = st.columns(3)

with col_get1:
    hotel_filter = st.selectbox(
        "Filter by Hotel Type", ["All", "City Hotel", "Resort Hotel"]
    )
with col_get2:
    limit = st.number_input(
        "Number of records (limit)", min_value=1, max_value=100, value=5
    )
with col_get3:
    skip = st.number_input("Records to skip (skip)", min_value=0, value=0)

if st.button("Execute GET Request"):
    params = {"skip": skip, "limit": limit}
    if hotel_filter != "All":
        params["hotel"] = hotel_filter

    try:
        response = requests.get(f"{API_URL}/bookings/", params=params, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            if data:
                st.success(f"Request successful. Retrieved {len(data)} records.")

                df_api = pd.DataFrame(data)
                st.subheader("Retrieved Data (DataFrame)")
                st.dataframe(df_api)

                st.subheader("Server Response (JSON)")
                st.json(data)
            else:
                st.info("No records found for the given parameters.")
        else:
            st.error(f"Server Error: Status code {response.status_code}")
    except Exception as e:
        st.error(f"Failed to connect to the FastAPI server. Error: {e}")

st.divider()

st.header("2. Create New Record (POST Request)")
st.markdown(
    "Fill out the form below to submit a new booking object to the dataset via the FastAPI endpoint."
)

with st.form("create_booking_form"):
    col_form1, col_form2, col_form3 = st.columns(3)

    with col_form1:
        hotel = st.selectbox("Hotel Type", ["City Hotel", "Resort Hotel"])
        lead_time = st.number_input("Lead Time (Days)", min_value=0, value=14)
        adr = st.number_input(
            "Average Daily Rate (ADR)", min_value=0.0, value=85.50, step=0.5
        )

    with col_form2:
        adults = st.number_input("Adults", min_value=1, value=2)
        children = st.number_input("Children", min_value=0, value=0)
        babies = st.number_input("Babies", min_value=0, value=0)

    with col_form3:
        weekend_nights = st.number_input("Weekend Nights", min_value=0, value=2)
        week_nights = st.number_input("Week Nights", min_value=0, value=3)
        special_requests = st.number_input("Special Requests", min_value=0, value=1)

    is_canceled = st.checkbox("Booking Canceled")

    submit_button = st.form_submit_button("Execute POST Request")

if submit_button:
    payload = {
        "hotel": hotel,
        "is_canceled": 1 if is_canceled else 0,
        "lead_time": int(lead_time),
        "adults": int(adults),
        "children": float(children),
        "babies": int(babies),
        "stays_in_weekend_nights": int(weekend_nights),
        "stays_in_week_nights": int(week_nights),
        "total_of_special_requests": int(special_requests),
        "adr": float(adr),
    }

    try:
        response = requests.post(f"{API_URL}/bookings/", json=payload, headers=HEADERS)

        if response.status_code == 200:
            created_booking = response.json()
            st.success("New booking successfully added to the database via API.")
            st.subheader("Data returned by the server")
            st.json(created_booking)
        else:
            st.error(f"Failed to create record. Status code: {response.status_code}")
            st.text(response.text)
    except Exception as e:
        st.error(f"Failed to connect to the FastAPI server. Error: {e}")
