import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hotel Booking Analysis", layout="wide")

st.title("Hotel Booking Data Analysis")

st.markdown("""
**Abstract:**
This project analyzes a dataset of hotel bookings to understand customer behavior, pricing trends, and cancellation factors. By utilizing exploratory data analysis (EDA) and statistical testing, we aim to uncover actionable insights for revenue management and operational staffing.

""")

st.divider()

st.header("1. Dataset Description & Initial Overview")
st.markdown(
    "Just like in our Jupyter Notebook, our first step is to load the raw dataset and examine its shape and data quality."
)


@st.cache_data
def load_raw_data():
    try:
        return pd.read_csv("data/raw/hotel_bookings.csv")
    except FileNotFoundError:
        return pd.read_csv("data/raw/hotel_bookings_extended.csv")


try:
    raw_df = load_raw_data()

    st.subheader("Raw Data Preview")
    st.dataframe(raw_df.head(), use_container_width=True)

    col_shape, col_missing = st.columns(2)
    with col_shape:
        st.subheader("Dataset Shape")
        st.info(f"Rows: {raw_df.shape[0]:,} \n\nColumns: {raw_df.shape[1]}")

    with col_missing:
        st.subheader("Missing Values Report")
        missing_data = raw_df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if not missing_data.empty:
            st.dataframe(missing_data.rename("Null Count"))
        else:
            st.success("No missing values detected.")

except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

st.divider()

st.header("2. Data Cleanup")
st.markdown("""
Based on the missing values report and domain logic, we apply the following data cleaning operations:
1. **Drop high-NaN columns:** The `company` and `agent` columns contain too many missing values to be useful.
2. **Remove invalid prices:** ADR (Average Daily Rate) cannot be less than or equal to 0.
3. **Remove ghost bookings:** Bookings where `adults` + `children` + `babies` == 0 are dropped.
4. **Handle missing categories:** Fill empty `country` values with 'Unknown'.
""")

with st.expander("🔍 View Python Cleaning Code"):
    st.code(
        """
    clean_df = raw_df.drop(columns=['company', 'agent'], errors='ignore')
    clean_df = clean_df[clean_df['adr'] > 0]
    clean_df = clean_df[(clean_df['adults'] + clean_df['children'] + clean_df['babies']) > 0]
    clean_df['country'] = clean_df['country'].fillna('Unknown')
    clean_df['children'] = clean_df['children'].fillna(0).astype(int)
    """,
        language="python",
    )

clean_df = raw_df.drop(columns=["company", "agent"], errors="ignore")
clean_df = clean_df[clean_df["adr"] > 0]
clean_df = clean_df[
    (clean_df["adults"] + clean_df["children"] + clean_df["babies"]) > 0
]
clean_df["country"] = clean_df["country"].fillna("Unknown")
clean_df["children"] = clean_df["children"].fillna(0).astype(int)

st.success(
    f"Data successfully cleaned! New shape: {clean_df.shape[0]:,} rows and {clean_df.shape[1]} columns."
)

st.divider()

st.header("3. Data Transformation")
st.markdown(
    "We engineer 3 new analytical columns derived from the existing dataset to aid our later hypothesis tests."
)

with st.expander("🔍 View Python Transformation Code"):
    st.code(
        """
    # 1. Calculate total stay duration
    clean_df['total_nights'] = clean_df['stays_in_weekend_nights'] + clean_df['stays_in_week_nights']
    
    # 2. Boolean flag for families
    clean_df['has_children'] = (clean_df['children'] > 0) | (clean_df['babies'] > 0)
    
    # 3. Boolean flag for demanding customers
    clean_df['has_special_requests'] = clean_df['total_of_special_requests'] > 0
    """,
        language="python",
    )

clean_df["total_nights"] = (
    clean_df["stays_in_weekend_nights"] + clean_df["stays_in_week_nights"]
)
clean_df["has_children"] = (clean_df["children"] > 0) | (clean_df["babies"] > 0)
clean_df["has_special_requests"] = clean_df["total_of_special_requests"] > 0

st.subheader("Transformed Dataset Preview")
st.dataframe(
    clean_df[
        ["hotel", "total_nights", "has_children", "has_special_requests", "adr"]
    ].head(),
    use_container_width=True,
)

st.divider()

st.header("4. Descriptive Statistics")
st.markdown(
    "We isolate 4 continuous numerical fields to analyze their central tendencies (Mean, Median) and dispersion (Standard Deviation)."
)

num_cols = ["lead_time", "adr", "stays_in_week_nights", "total_of_special_requests"]
stats_df = clean_df[num_cols].describe().T
st.dataframe(stats_df, use_container_width=True)

st.session_state["df"] = clean_df
