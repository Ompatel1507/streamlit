import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config for wide layout
st.set_page_config(
    page_title="SuperStore KPI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS for Modern UI ----
st.markdown(
    """
    <style>
    /* Main background and font */
    body {
        background-color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }

    /* Header styling */
    .header {
        font-size: 36px;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        padding: 20px;
        background-color: #ffffff;
        border-bottom: 2px solid #e0e0e0;
    }

    /* KPI tiles */
    .kpi-box {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .kpi-title {
        font-weight: 600;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-weight: 700;
        font-size: 28px;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    .sidebar .stSelectbox, .sidebar .stDateInput {
        background-color: #34495e;
        color: white;
        border-radius: 8px;
        padding: 8px;
    }

    /* Button styling */
    .stButton button {
        background-color: #2575fc;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #1a5bbf;
    }

    /* Chart styling */
    .stPlotlyChart {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Dark mode toggle */
    .dark-mode .kpi-box {
        background: linear-gradient(135deg, #34495e, #2c3e50);
    }
    .dark-mode .header {
        background-color: #2c3e50;
        color: white;
    }
    .dark-mode body {
        background-color: #1a1a1a;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Dark Mode Toggle ----
dark_mode = st.sidebar.checkbox("Dark Mode")

if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #1a1a1a;
            color: white;
        }
        .kpi-box {
            background: linear-gradient(135deg, #34495e, #2c3e50);
        }
        .header {
            background-color: #2c3e50;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---- Header ----
st.markdown(
    """
    <div class="header">
        SuperStore KPI Dashboard
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df_original = load_data()

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

# Region Filter
all_regions = sorted(df_original["Region"].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + all_regions)

# Filter data by Region
if selected_region != "All":
    df_filtered_region = df_original[df_original["Region"] == selected_region]
else:
    df_filtered_region = df_original

# State Filter
all_states = sorted(df_filtered_region["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", options=["All"] + all_states)

# Filter data by State
if selected_state != "All":
    df_filtered_state = df_filtered_region[df_filtered_region["State"] == selected_state]
else:
    df_filtered_state = df_filtered_region

# Category Filter
all_categories = sorted(df_filtered_state["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", options=["All"] + all_categories)

# Filter data by Category
if selected_category != "All":
    df_filtered_category = df_filtered_state[df_filtered_state["Category"] == selected_category]
else:
    df_filtered_category = df_filtered_state

# Sub-Category Filter
all_subcats = sorted(df_filtered_category["Sub-Category"].dropna().unique())
selected_subcat = st.sidebar.selectbox("Select Sub-Category", options=["All"] + all_subcats)

# Final filter by Sub-Category
df = df_filtered_category.copy()
if selected_subcat != "All":
    df = df[df["Sub-Category"] == selected_subcat]

# ---- Sidebar Date Range (From and To) ----
if df.empty:
    min_date = df_original["Order Date"].min()
    max_date = df_original["Order Date"].max()
else:
    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()

from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

if from_date > to_date:
    st.sidebar.error("From Date must be earlier than To Date.")

df = df[(df["Order Date"] >= pd.to_datetime(from_date)) & (df["Order Date"] <= pd.to_datetime(to_date))]

# ---- KPI Calculation ----
if df.empty:
    total_sales = 0
    total_quantity = 0
    total_profit = 0
    margin_rate = 0
else:
    total_sales = df["Sales"].sum()
    total_quantity = df["Quantity"].sum()
    total_profit = df["Profit"].sum()
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

# ---- KPI Display (Rectangles) ----
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Sales</div>
            <div class='kpi-value'>${total_sales:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col2:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Quantity Sold</div>
            <div class='kpi-value'>{total_quantity:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col3:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Profit</div>
            <div class='kpi-value'>${total_profit:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col4:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Margin Rate</div>
            <div class='kpi-value'>{(margin_rate * 100):,.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- Data Export ----
if st.button("Export Filtered Data as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )

# ---- KPI Selection (Affects Both Charts) ----
st.subheader("Visualize KPI Across Time & Top Products")

if df.empty:
    st.warning("No data available for the selected filters and date range. Please adjust your filters.")
else:
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to display:", options=kpi_options, horizontal=True)

    # ---- Prepare Data for Charts ----
    daily_grouped = df.groupby("Order Date").agg({
        "Sales": "sum",
        "Quantity": "sum",
        "Profit": "sum"
    }).reset_index()
    daily_grouped["Margin Rate"] = daily_grouped["Profit"] / daily_grouped["Sales"].replace(0, 1)

    product_grouped = df.groupby("Product Name").agg({
        "Sales": "sum",
        "Quantity": "sum",
        "Profit": "sum"
    }).reset_index()
    product_grouped["Margin Rate"] = product_grouped["Profit"] / product_grouped["Sales"].replace(0, 1)

    product_grouped.sort_values(by=selected_kpi, ascending=False, inplace=True)
    top_10 = product_grouped.head(10)

    # ---- Side-by-Side Layout for Charts ----
    col_left, col_right = st.columns(2)

    with col_left:
        fig_line = px.line(
            daily_grouped,
            x="Order Date",
            y=selected_kpi,
            title=f"{selected_kpi} Over Time",
            labels={"Order Date": "Date", selected_kpi: selected_kpi},
            template="plotly_white",
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        fig_bar = px.bar(
            top_10,
            x=selected_kpi,
            y="Product Name",
            orientation="h",
            title=f"Top 10 Products by {selected_kpi}",
            labels={selected_kpi: selected_kpi, "Product Name": "Product"},
            color=selected_kpi,
            color_continuous_scale="Blues",
            template="plotly_white",
        )
        fig_bar.update_layout(
            height=400,
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ---- Contextual Insights ----
st.subheader("Contextual Insights")
if not df.empty:
    previous_period_sales = df_original[
        (df_original["Order Date"] >= pd.to_datetime(from_date) - pd.Timedelta(days=30)) &
        (df_original["Order Date"] < pd.to_datetime(from_date))
    ]["Sales"].sum()
    sales_change = ((total_sales - previous_period_sales) / previous_period_sales) * 100 if previous_period_sales != 0 else 0
    st.metric("Sales Change vs Previous 30 Days", f"{sales_change:.2f}%")

# ---- Additional Enhancements ----
# 1. Add a benchmark comparison
benchmark_sales = df_original["Sales"].mean()
st.metric("Benchmark Sales", f"${benchmark_sales:,.2f}")

# 2. Add a heatmap for sales by category and sub-category
heatmap_data = df.groupby(["Category", "Sub-Category"]).agg({"Sales": "sum"}).reset_index()
fig_heatmap = px.density_heatmap(
    heatmap_data,
    x="Category",
    y="Sub-Category",
    z="Sales",
    title="Sales Heatmap by Category and Sub-Category",
    template="plotly_white",
)
st.plotly_chart(fig_heatmap, use_container_width=True)
