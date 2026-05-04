import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import fetch_data
from data_utils import process_data
from kerala_map import KERALA_MAP

st.set_page_config(layout="wide")

st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 10px;
    color: white;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("Kerala Election 2026 Dashboard")

df = fetch_data()

if df.empty:
    st.warning("No data available")
    st.stop()

df["District"] = df["Constituency"].map(KERALA_MAP)

df, winners, seat_count = process_data(df)

# 🔍 FILTERS
st.sidebar.header("Filters")

districts = ["All"] + sorted(df["District"].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("District", districts)

filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

parties = ["All"] + sorted(filtered_df["Party"].unique().tolist())
selected_party = st.sidebar.selectbox("Party", parties)

if selected_party != "All":
    filtered_df = filtered_df[filtered_df["Party"] == selected_party]

constituencies = ["All"] + sorted(filtered_df["Constituency"].unique().tolist())
selected_constituency = st.sidebar.selectbox("Constituency", constituencies)

if selected_constituency != "All":
    filtered_df = filtered_df[filtered_df["Constituency"] == selected_constituency]

# 🔥 TOP CARDS
st.subheader("Party Leading Status")

card_colors = {
    "INC": "#3498db",
    "CPI(M)": "#e74c3c",
    "IUML": "#2ecc71",
    "CPI": "#c0392b",
    "BJP": "#e67e22",
    "Others": "#7f8c8d"
}

cols = st.columns(len(seat_count))

for i, (party, count) in enumerate(seat_count.items()):
    color = card_colors.get(party, "#9b59b6")
    cols[i].markdown(f"""
        <div class="card" style="background-color:{color}">
            {party}<br><h2>{count}</h2>
        </div>
    """, unsafe_allow_html=True)

# 🔥 MAIN LAYOUT
left, right = st.columns([2, 1])

with left:
    st.subheader("Constituency Results")
    st.dataframe(filtered_df, use_container_width=True)

with right:
    st.subheader("District Vote Overview")
    district_votes = filtered_df.groupby("District")["Votes"].sum().reset_index()

    fig_map = px.bar(
        district_votes,
        x="District",
        y="Votes",
        color="Votes"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 🔥 CHARTS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Seat Distribution")
    fig1 = px.pie(
        values=seat_count.values,
        names=seat_count.index,
        hole=0.5
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Vote Share")
    vote_share = filtered_df.groupby("Party")["Votes"].sum().reset_index()
    fig2 = px.pie(
        vote_share,
        values="Votes",
        names="Party"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div style='text-align:center'>
    <button style='background-color:#2c7be5;color:white;padding:10px 30px;border:none;border-radius:5px'>
        All Constituencies at a glance >
    </button>
</div>
""", unsafe_allow_html=True)
