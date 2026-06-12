import streamlit as st
import pandas as pd
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.cleaning import load_raw_data, clean_data

st.set_page_config(page_title="Hotel Booking Analysis", layout="wide")

st.title("Hotel Booking Analysis")

st.markdown("""
### Abstract / Annotation
This project explores a comprehensive hotel booking dataset containing reservations for both City Hotels and Resort Hotels. The primary objective is to perform data cleanup, visualize key booking trends, and statistically evaluate hypotheses regarding customer behavior. Key metrics analyzed include the length of stay, average daily rate (ADR), lead time, and the impact of special requests and family composition on booking outcomes.

**Team Contribution:**
* **Andrew:** Handled everything.
""")

st.divider()

st.header("1. Dataset Description & Raw Data")
st.markdown(
    "The dataset contains booking information for a city hotel and a resort hotel, including details such as when the booking was made, length of stay, the number of adults, children, and/or babies, and the number of available parking spaces."
)


@st.cache_data
def get_raw():
    return load_raw_data()


raw_df = get_raw()
st.write(
    f"**Initial Dataset Shape:** `{raw_df.shape[0]} rows`, `{raw_df.shape[1]} columns`"
)

missing_data = raw_df.isnull().sum()
missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
if not missing_data.empty:
    st.markdown("**Missing Values Identified:**")
    st.dataframe(missing_data, column_config={"value": "Missing Count"})

st.divider()

st.header("2. Data Cleanup")
st.markdown(
    "To prepare the dataset for analysis, we address the missing values and logical inconsistencies."
)
st.code(
    """
# 1. Fill missing 'children' with 0
# 2. Fill missing 'country' with 'Unknown'
# 3. Drop columns with excessive missing values ('company', 'agent')
# 4. Remove duplicate rows
""",
    language="python",
)


@st.cache_data
def get_cleaned():
    return clean_data(raw_df)


clean_df = get_cleaned()

st.divider()

st.header("3. Data Transformation")
st.markdown(
    "We engineer three new analytical columns to facilitate our hypothesis testing and visualizations."
)
st.code(
    """
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['has_children'] = (df['children'] > 0) | (df['babies'] > 0)
df['has_special_requests'] = df['total_of_special_requests'] > 0
""",
    language="python",
)

clean_df["total_nights"] = (
    clean_df["stays_in_weekend_nights"] + clean_df["stays_in_week_nights"]
)
clean_df["has_children"] = (clean_df["children"] > 0) | (clean_df["babies"] > 0)
clean_df["has_special_requests"] = clean_df["total_of_special_requests"] > 0

st.session_state["df"] = clean_df

st.divider()

st.header("4. Descriptive Statistics")
st.markdown(
    "Standard descriptive statistics (mean, standard deviation, percentiles) for our key numerical fields."
)
st.dataframe(
    clean_df[
        ["lead_time", "total_nights", "adr", "total_of_special_requests"]
    ].describe()
)

st.info(
    "Pipeline complete. Navigate to the next pages using the sidebar for visual and statistical analysis."
)
