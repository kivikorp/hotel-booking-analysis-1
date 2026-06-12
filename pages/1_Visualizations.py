import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Overview", layout="wide")
st.title("Exploratory Data Analysis")

if "df" not in st.session_state:
    st.warning("Please load the data on the Home page first.")
    st.stop()

df = st.session_state["df"]

st.header("General Overview")
st.markdown("Visualizing the fundamental shape of our four core numerical fields.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Distribution of Lead Time**")
    fig_lead = px.histogram(df, x="lead_time", nbins=50)
    st.plotly_chart(fig_lead, use_container_width=True)

    st.markdown("**Spread of Average Daily Rate (ADR)**")
    fig_adr = px.box(df, y="adr")
    fig_adr.update_yaxes(range=[0, 500])
    st.plotly_chart(fig_adr, use_container_width=True)

with col2:
    st.markdown("**Distribution of Week Nights Stayed**")
    fig_nights = px.histogram(df, x="stays_in_week_nights", nbins=30)
    fig_nights.update_xaxes(range=[0, 15])
    st.plotly_chart(fig_nights, use_container_width=True)

    st.markdown("**Frequency of Special Requests**")
    req_counts = df["total_of_special_requests"].value_counts().reset_index()
    req_counts.columns = ["Requests", "Count"]
    fig_req = px.bar(req_counts, x="Requests", y="Count")
    st.plotly_chart(fig_req, use_container_width=True)

st.divider()

st.header("Detailed Overview")
st.markdown("Complex relations, subset comparisons, and correlations.")

st.markdown("**1. Lead Time vs. ADR by Hotel Type**")
sample_df = df.sample(n=5000, random_state=42) if len(df) > 5000 else df
fig_scatter = px.scatter(sample_df, x="lead_time", y="adr", color="hotel", opacity=0.5)
fig_scatter.update_yaxes(range=[0, 500])
st.plotly_chart(fig_scatter, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**2. ADR by Customer Type (Split by Cancellation)**")
    fig_box2 = px.box(df, x="customer_type", y="adr", color="is_canceled")
    fig_box2.update_yaxes(range=[0, 400])
    st.plotly_chart(fig_box2, use_container_width=True)

with col4:
    st.markdown("**3. Correlation Matrix of Numerical Features**")
    num_cols = [
        "lead_time",
        "total_nights",
        "adr",
        "total_of_special_requests",
        "is_canceled",
    ]
    corr_matrix = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, vmin=-1, vmax=1
    )
    st.pyplot(fig)

st.markdown("**4. Subset Statistics Summary**")
subset_stats = (
    df.groupby(["hotel", "distribution_channel"])[["adr", "lead_time"]]
    .median()
    .reset_index()
)
subset_stats.columns = ["Hotel Type", "Channel", "Median ADR", "Median Lead Time"]
st.dataframe(subset_stats, use_container_width=True)
