import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ---- STREAMLIT PAGE CONFIG ----
st.set_page_config(
    page_title="Flight Delay Dashboard",
    page_icon="✈️",
    layout="wide",
)

st.markdown(
    """
    <style>
        body {background-color: #1E1E1E; color: white;}
        .st-bj {background-color: #262730 !important;}
        .st-bc {color: white !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- TITLE ----
st.markdown("<h1 style='text-align: center; color: cyan;'>✈️ Flight Delay Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: lightgray;'>US Airline delay insights powered by CSV & Streamlit (2024)</h3>", unsafe_allow_html=True)

# ---- LOAD DATA FROM CSV ----
@st.cache_data
def load_data():
    return pd.read_csv("Airline_Delay_Cause.csv")

df = load_data()

# ---- FETCH UNIQUE AIRLINES & AIRPORTS FOR DROPDOWN ----
airline_options = ["All"] + sorted(df["carrier_name"].dropna().unique().tolist())
airport_options = ["All"] + sorted(df["airport_name"].dropna().unique().tolist())

# ---- SIDEBAR FILTERS ----
st.sidebar.header("🔍 Filters")

# Airline Dropdown
selected_airline = st.sidebar.selectbox("✈️ Select Airline", airline_options)

# Airport Dropdown
selected_airport = st.sidebar.selectbox("📍 Select Airport", airport_options)

# ---- APPLY FILTERS ----
filtered_df = df.copy()
if selected_airline != "All":
    filtered_df = filtered_df[filtered_df["carrier_name"] == selected_airline]
if selected_airport != "All":
    filtered_df = filtered_df[filtered_df["airport_name"] == selected_airport]

# ---- 1️⃣ WORST AIRPORTS ----
df_airports = (
    filtered_df.groupby("airport_name")["arr_del15"]
    .sum()
    .reset_index()
    .rename(columns={"arr_del15": "total_delays"})
    .sort_values(by="total_delays", ascending=False)
    .head(10)
)

# ---- 2️⃣ WORST AIRLINES ----
df_airlines = (
    filtered_df.groupby("carrier_name")["arr_del15"]
    .sum()
    .reset_index()
    .rename(columns={"arr_del15": "total_delays"})
    .sort_values(by="total_delays", ascending=False)
    .head(10)
)

# ---- 3️⃣ AVERAGE DELAY PER AIRLINE ----
df_avg_delay = (
    filtered_df.groupby("carrier_name")["arr_delay"]
    .mean()
    .reset_index()
    .rename(columns={"arr_delay": "avg_delay_minutes"})
    .sort_values(by="avg_delay_minutes", ascending=False)
    .head(10)
)

# ---- 4️⃣ DELAY CAUSES ----
df_delay_causes = (
    filtered_df[["carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]]
    .sum()
    .reset_index()
    .rename(columns={0: "Total Delays"})
)
df_delay_causes.columns = ["Cause", "Total Delays"]

# ---- 5️⃣ MONTHLY DELAY TRENDS ----
df_monthly = (
    filtered_df.groupby("month")["arr_del15"]
    .sum()
    .reset_index()
    .rename(columns={"arr_del15": "total_delays"})
    .sort_values(by="month")
)

# ---- PLOTS ----
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📍 Worst Airports for Delays")
    fig_airports = px.bar(df_airports, x="total_delays", y="airport_name", orientation="h", color="total_delays",
                          color_continuous_scale="reds", title="Top 10 Airports with Most Delays")
    st.plotly_chart(fig_airports, use_container_width=True)

with col2:
    st.markdown("### 🏢 Worst Airlines for Delays")
    fig_airlines = px.bar(df_airlines, x="total_delays", y="carrier_name", orientation="h", color="total_delays",
                          color_continuous_scale="blues", title="Top 10 Airlines with Most Delays")
    st.plotly_chart(fig_airlines, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.markdown("### ⏳ Average Delay Time by Airline")
    fig_avg_delays = px.bar(df_avg_delay, x="avg_delay_minutes", y="carrier_name", orientation="h", color="avg_delay_minutes",
                            color_continuous_scale="purples", title="Airlines with the Longest Average Delays")
    st.plotly_chart(fig_avg_delays, use_container_width=True)

with col4:
    st.markdown("### ⛅ Causes of Flight Delays")
    fig_delay_causes = px.pie(df_delay_causes, names="Cause", values="Total Delays", title="Breakdown of Flight Delay Causes",
                              color_discrete_sequence=px.colors.sequential.Oranges)
    st.plotly_chart(fig_delay_causes, use_container_width=True)

st.markdown("---")

st.markdown("### 📅 Monthly Delay Trends")
fig_monthly = px.line(df_monthly, x="month", y="total_delays", markers=True, color_discrete_sequence=["red"])
fig_monthly.update_xaxes(title_text="Month")
fig_monthly.update_yaxes(title_text="Total Delays")
st.plotly_chart(fig_monthly, use_container_width=True)

# ---- FOOTER ----
st.markdown("<h5 style='text-align: center; color: lightgray;'>Built using Streamlit & CSV</h5>", unsafe_allow_html=True)
