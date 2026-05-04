import streamlit as st
import pandas as pd
import time
import plotly.express as px

from scraper import fetch_data
from data_utils import process_data

try:
    from photos import get_candidate_photo
except:
    def get_candidate_photo(name):
        return "https://via.placeholder.com/100"

try:
    from kerala_map import KERALA_MAP
except:
    KERALA_MAP = {}

# ---------------- UI ----------------
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗳️ Kerala Election 2026 LIVE Tracker")
st.markdown("### Real-time insights & analytics dashboard")

# auto refresh
st.markdown("<meta http-equiv='refresh' content='20'>", unsafe_allow_html=True)

# ---------------- Data ----------------
def add_district(df):
    if "Constituency" in df.columns:
        df["District"] = df["Constituency"].map(KERALA_MAP)
    return df

with st.spinner("Fetching live election data..."):
    raw_df = fetch_data()

if raw_df is None or raw_df.empty:
    st.warning("⏳ Waiting for data...")
    st.stop()

df, winners, seat_count = process_data(raw_df)
df = add_district(df)

df = df.dropna(subset=["Constituency", "Party"])

# ---------------- Sidebar ----------------
st.sidebar.header("🔍 Filters")

districts = ["All"] + sorted(df["District"].dropna().unique().tolist())
constituencies = ["All"] + sorted(df["Constituency"].unique().tolist())
parties = ["All"] + sorted(df["Party"].unique().tolist())

selected_district = st.sidebar.selectbox("District", districts)
selected_constituency = st.sidebar.selectbox("Constituency", constituencies)
selected_party = st.sidebar.selectbox("Party", parties)

filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_constituency != "All":
    filtered_df = filtered_df[filtered_df["Constituency"] == selected_constituency]

if selected_party != "All":
    filtered_df = filtered_df[filtered_df["Party"] == selected_party]

# ---------------- Info ----------------
st.caption(f"⏱️ Last Updated: {time.strftime('%H:%M:%S')}")

# ---------------- Insights ----------------
st.subheader("🧠 Key Insights")

top_party = seat_count.idxmax()
st.success(f"🔥 Leading Party: {top_party}")

top_candidate = winners.loc[winners["Votes"].idxmax()]
st.info(f"🏆 Top Candidate: {top_candidate['Candidate']} ({top_candidate['Votes']} votes)")

# ---------------- Charts ----------------
st.subheader("📊 Seat Distribution")
fig1 = px.pie(values=seat_count.values, names=seat_count.index)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📊 Votes by Party")
party_votes = df.groupby("Party")["Votes"].sum().reset_index()
fig2 = px.bar(party_votes, x="Party", y="Votes", color="Party")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🗺️ District-wise Votes")
district_votes = df.groupby("District")["Votes"].sum().reset_index()
fig3 = px.bar(district_votes, x="District", y="Votes", color="Votes")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- Table ----------------
st.subheader("📊 Live Results")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- Winners ----------------
st.subheader("🏆 Leading Candidates")
st.dataframe(winners, use_container_width=True)

# ---------------- Candidate Cards ----------------
st.subheader("🧑‍💼 Candidate Highlights")

cols = st.columns(4)

for i, row in winners.iterrows():
    with cols[i % 4]:
        img = get_candidate_photo(row["Candidate"])
        st.image(img, width=100)
        st.markdown(f"""
        **{row['Candidate']}**  
        🏛 {row['Party']}  
        🗳 {row['Votes']} votes  
        📍 {row.get('District','N/A')}
        """)

# ---------------- Trend ----------------
import numpy as np

st.subheader("📈 Vote Trend (Simulation)")
trend = np.cumsum(np.random.randint(100, 500, 20))
st.line_chart(trend)
