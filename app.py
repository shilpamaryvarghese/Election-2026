import streamlit as st
import pandas as pd
import time

from scraper import fetch_data
from data_utils import process_data

# Optional photo support
try:
    from photos import get_candidate_photo
except:
    def get_candidate_photo(name):
        return "https://via.placeholder.com/100"

st.set_page_config(layout="wide")

st.title("🗳️ Kerala Election 2026 - LIVE Dashboard")

# 🔄 Auto refresh every 60 sec
st.markdown(
    "<meta http-equiv='refresh' content='60'>",
    unsafe_allow_html=True
)

st.sidebar.header("🔍 Filters")

try:
    raw_df = fetch_data()

    if raw_df is None or raw_df.empty:
        st.warning("⏳ Waiting for live election data...")
        st.stop()

    df, winners, seat_count = process_data(raw_df)

    # 🎯 FILTERS
    constituencies = ["All"] + sorted(df["Constituency"].unique().tolist())
    parties = ["All"] + sorted(df["Party"].unique().tolist())

    selected_constituency = st.sidebar.selectbox("Constituency", constituencies)
    selected_party = st.sidebar.selectbox("Party", parties)

    filtered_df = df.copy()

    if selected_constituency != "All":
        filtered_df = filtered_df[filtered_df["Constituency"] == selected_constituency]

    if selected_party != "All":
        filtered_df = filtered_df[filtered_df["Party"] == selected_party]

    # ⏱️ Timestamp
    st.caption(f"⏱️ Last Updated: {time.strftime('%H:%M:%S')}")

    # 📊 TABLE
    st.subheader("📊 Constituency Results")
    st.dataframe(filtered_df, use_container_width=True)

    # 🏆 LEADING
    st.subheader("🏆 Candidates")
    st.dataframe(winners, use_container_width=True)

    # 📺 PARTY SEATS
    st.subheader("📺 Party Seat Count")
    st.bar_chart(seat_count)

    # 📊 PARTY VOTES
    st.subheader("📊 Total Votes by Party")
    party_votes = df.groupby("Party")["Votes"].sum()
    st.bar_chart(party_votes)

    # 🧑‍💼 Candidate Cards
    st.subheader("🧑‍💼 Candidate Details")

    cols = st.columns(4)

    for i, row in winners.iterrows():
        with cols[i % 4]:
            img = get_candidate_photo(row["Candidate"])
            st.image(img, width=100)
            st.markdown(f"**{row['Candidate']}**")
            st.write(f"Party: {row['Party']}")
            st.write(f"Votes: {row['Votes']}")

except Exception as e:
    st.error(f"⚠️ Error: {e}")
