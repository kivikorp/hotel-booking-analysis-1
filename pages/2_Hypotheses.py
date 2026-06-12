import streamlit as st
import pandas as pd
from scipy import stats

st.set_page_config(page_title="Hypothesis Testing", layout="wide")
st.title("Hypothesis Testing")

if "df" not in st.session_state:
    st.warning("Please load the data on the Home page first.")
    st.stop()

df = st.session_state["df"]

st.header("Statistical Analysis")
st.markdown(
    "Visualizations can imply trends, but statistical rigor is required to confirm them. We use the `scipy.stats` library to test our two primary observations."
)

st.divider()

st.subheader("Hypothesis 1: Impact of Children on Stay Duration")
st.markdown("""
* **Null Hypothesis (H0):** There is no difference in the mean total nights stayed between guests with children and guests without.
* **Test Chosen:** Independent two-sample T-test (Welch's).
""")

group_children = df[df["has_children"] == True]["total_nights"]
group_no_children = df[df["has_children"] == False]["total_nights"]

t_stat, p_val = stats.ttest_ind(
    group_children, group_no_children, equal_var=False, nan_policy="omit"
)

c1, c2 = st.columns(2)
c1.metric("Avg Stay (With Children)", f"{group_children.mean():.2f} nights")
c2.metric("Avg Stay (Without Children)", f"{group_no_children.mean():.2f} nights")

st.write(f"**T-Statistic:** `{t_stat:.4f}` | **P-Value:** `{p_val:.4e}`")

if p_val < 0.05:
    st.info(
        "Conclusion: Reject the null hypothesis. The visual trend is confirmed statistically: guests with children stay significantly longer."
    )
else:
    st.info("Conclusion: Fail to reject the null hypothesis.")

st.divider()

st.subheader("Hypothesis 2: Special Requests and Cancellations")
st.markdown("""
* **Null Hypothesis (H0):** Booking cancellation is completely independent of whether a guest makes special requests.
* **Test Chosen:** Chi-Square Test of Independence.
""")

contingency_table = pd.crosstab(df["has_special_requests"], df["is_canceled"])
st.write("Contingency Table (Columns: is_canceled 0/1):")
st.dataframe(contingency_table)

chi2, p_val_2, dof, expected = stats.chi2_contingency(contingency_table)

st.write(f"**Chi-Square Statistic:** `{chi2:.4f}` | **P-Value:** `{p_val_2:.4e}`")

if p_val_2 < 0.05:
    st.info(
        "Conclusion: Reject the null hypothesis. There is a strong dependence between making special requests and not canceling."
    )
else:
    st.info("Conclusion: Fail to reject the null hypothesis.")
