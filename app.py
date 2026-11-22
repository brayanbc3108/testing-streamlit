# Testing Streamlit: sellers dashboard
# Run with: uv run streamlit run app.py

import pandas as pd
import streamlit as st

# Page setup: title shown in the browser tab and a wide layout
st.set_page_config(page_title="Sellers Dashboard", layout="wide")


# Read the Excel file once and keep it in cache so it is not reloaded on every click
@st.cache_data
def load_data():
    df = pd.read_excel("sellers.xlsx")
    # Build a single readable name column for the vendor selector
    df["FULL NAME"] = df["NAME"] + " " + df["LASTNAME"]
    return df


df = load_data()

st.title("Sellers Dashboard")

# ---------------------------------------------------------------
# Sidebar: region filter (multiselect, all regions selected at start)
# ---------------------------------------------------------------
st.sidebar.header("Filters")
regions = sorted(df["REGION"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

# Keep only the rows that belong to the selected regions
filtered = df[df["REGION"].isin(selected_regions)]

# Stop early if nothing is selected so the charts do not break
if filtered.empty:
    st.warning("Select at least one region.")
    st.stop()

# ---------------------------------------------------------------
# Section 1: KPIs and table filtered by region
# ---------------------------------------------------------------
with st.container():
    st.subheader("Table by region")

    # Four summary numbers for the filtered data
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sellers", len(filtered))
    c2.metric("Units sold", f"{filtered['SOLD UNITS'].sum():,}")
    c3.metric("Total sales", f"{filtered['TOTAL SALES'].sum():,}")
    c4.metric("Average sales", f"{filtered['SALES AVERAGE'].mean():.3f}")

    # Show the table; the button hides or shows it
    if st.button("Show / hide table"):
        st.session_state["show_table"] = not st.session_state.get("show_table", True)
    if st.session_state.get("show_table", True):
        st.dataframe(filtered.drop(columns="FULL NAME"), width="stretch")

# ---------------------------------------------------------------
# Section 2: graphs of Units Sold, Total Sales and Average Sales
# Default Streamlit chart settings on purpose (this is a sketch)
# ---------------------------------------------------------------
with st.container():
    st.subheader("Graphs")

    # One tab per metric, grouped by region
    tab1, tab2, tab3 = st.tabs(["Units Sold", "Total Sales", "Average Sales"])

    with tab1:
        st.bar_chart(filtered.groupby("REGION")["SOLD UNITS"].sum())
    with tab2:
        st.bar_chart(filtered.groupby("REGION")["TOTAL SALES"].sum())
    with tab3:
        st.bar_chart(filtered.groupby("REGION")["SALES AVERAGE"].mean())

    # Per seller view of the same metrics
    metric = st.selectbox("Metric per seller", ["SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"])
    st.bar_chart(filtered.set_index("FULL NAME")[metric])

# ---------------------------------------------------------------
# Section 3: data for a specific vendor
# ---------------------------------------------------------------
with st.container():
    st.subheader("Vendor detail")

    # The selector lists only the vendors of the selected regions
    vendor = st.selectbox("Choose a vendor", filtered["FULL NAME"])
    row = filtered[filtered["FULL NAME"] == vendor].iloc[0]

    st.write(f"**{vendor}** | Region: {row['REGION']} | ID: {row['ID']}")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Income", f"{row['INCOME']:,}")
    v2.metric("Units sold", f"{row['SOLD UNITS']:,}")
    v3.metric("Total sales", f"{row['TOTAL SALES']:,}")
    v4.metric("Average sales", f"{row['SALES AVERAGE']:.3f}")

    # Compare the vendor against the average of the selected regions
    comparison = pd.DataFrame(
        {
            vendor: [row["SOLD UNITS"], row["TOTAL SALES"]],
            "Average of selection": [
                filtered["SOLD UNITS"].mean(),
                filtered["TOTAL SALES"].mean(),
            ],
        },
        index=["SOLD UNITS", "TOTAL SALES"],
    )
    st.bar_chart(comparison)
