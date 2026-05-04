import streamlit as st
import pandas as pd
import time

from scraper import fetch_data
from data_utils import process_data

# Optional imports (avoid crash if missing)
try:
    from photos import get_candidate_photo
except:
    def get_candidate_photo(name):
        return "https://via.placeholder.com/100"

try:
    from kerala_map import KERALA_MAP
except:
    KERALA_MAP = {}

st.set_page_config(layout="wide")

st.title("🗳️ Kerala Election 2026 - LIVE Dashboard")

# 🔄 Auto refresh every 15 sec (SAFE)
st.markdown(
    "<meta http-equiv='refresh' content='15'>",
    unsafe_allow_html=True
)

st.sidebar.header("🔍 Filters")

def add_district(df):
    if "Constituency" in df.columns:
        df["District"] = df["Constituency"].map(KERALA_MAP)
    return df

try:
    raw_df = fetch_data()

    # 🚨 Handle empty
    if raw_df is None or raw_df.empty:
        st.warning("⏳ Waiting for live election data...")
        st.stop()

    df, winners, seat_count = process_data(raw_df)

    # 🗺️ Add district
    df = add_district(df)

    # Clean data
    df = df.dropna(subset=["Constituency", "Party"])
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

    # 🧠 FILTER OPTIONS
    districts = ["All"] + sorted(df.get("District", pd.Series()).dropna().unique().tolist())
    constituencies = ["All"] + sorted(df["Constituency"].unique().tolist())
    parties = ["All"] + sorted(df["Party"].unique().tolist())

    # 🎯 Filters
    selected_district = st.sidebar.selectbox("District", districts)
    selected_constituency = st.sidebar.selectbox("Constituency", constituencies)
    selected_party = st.sidebar.selectbox("Party", parties)

    # Apply filters
    filtered_df = df.copy()

    if selected_district != "All":
        filtered_df = filtered_df[filtered_df["District"] == selected_district]

    if selected_constituency != "All":
        filtered_df = filtered_df[filtered_df["Constituency"] == selected_constituency]

    if selected_party != "All":
        filtered_df = filtered_df[filtered_df["Party"] == selected_party]

    # ⏱️ Timestamp
    st.caption(f"⏱️ Last Updated: {time.strftime('%H:%M:%S')}")

    # 📊 MAIN TABLE
    st.subheader("📊 Constituency-wise Live Results")
    st.dataframe(filtered_df, use_container_width=True)

    # 🏆 WINNERS
    if winners is not None and not winners.empty:
        st.subheader("🏆 Leading Candidates")
        st.dataframe(winners, use_container_width=True)

    # 📺 SEAT COUNT
    if seat_count is not None and not seat_count.empty:
        st.subheader("📺 Party Seat Count")
        st.bar_chart(seat_count)

    # 📊 PARTY VOTES
    if not df.empty:
        st.subheader("📊 Total Votes by Party")
        party_votes = df.groupby("Party")["Votes"].sum()
        st.bar_chart(party_votes)

    # 🗺️ DISTRICT TOTALS
    if "District" in df.columns:
        st.subheader("🗺️ District-wise Vote Totals")
        district_votes = df.groupby("District")["Votes"].sum()
        st.bar_chart(district_votes)

    # 🏆 DISTRICT LEADERS
    if "District" in df.columns:
        st.subheader("🏆 District Leaders")
        district_leaders = df.loc[df.groupby("District")["Votes"].idxmax()]
        st.dataframe(district_leaders)

    # 📊 PIVOT TABLE
    st.subheader("📊 Party-wise Votes per Constituency")
    pivot = df.pivot_table(
        index="Constituency",
        columns="Party",
        values="Votes",
        aggfunc="sum"
    ).fillna(0)

    st.dataframe(pivot, use_container_width=True)

    # 🧑‍💼 CANDIDATE CARDS
    if winners is not None and not winners.empty:
        st.subheader("🧑‍💼 Candidate Details")

        cols = st.columns(4)

        for i, row in winners.iterrows():
            with cols[i % 4]:
                img = get_candidate_photo(row["Candidate"])
                st.image(img, width=100)
                st.markdown(f"**{row['Candidate']}**")
                st.write(f"Party: {row['Party']}")
                st.write(f"Votes: {row['Votes']}")
                st.write(f"District: {row.get('District','N/A')}")

except Exception as e:
    st.error(f"⚠️ Error fetching data: {e}")
