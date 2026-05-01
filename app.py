import streamlit as st
import pandas as pd
import time

from scraper import fetch_live_results
from data_utils import process_data
from photos import get_candidate_photo
from kerala_map import KERALA_MAP   # 👈 NEW

st.set_page_config(layout="wide")

st.title("🗳️ Kerala Election 2026 - LIVE Dashboard")

st.sidebar.header("🔍 Filters")

placeholder = st.empty()

def add_district(df):
    df["District"] = df["Constituency"].map(KERALA_MAP)
    return df

while True:
    try:
        raw_df = fetch_live_results()

        # 🚨 Handle no data
        if raw_df is None or raw_df.empty:
            with placeholder.container():
                st.warning("⏳ Waiting for live election data...")
            time.sleep(5)
            st.rerun()

        df, winners, seat_count = process_data(raw_df)

        # 🗺️ Add district
        df = add_district(df)

        # Clean data
        df = df.dropna(subset=["Constituency", "Party"])
        df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

        # 🧠 FILTER OPTIONS
        districts = ["All"]
        constituencies = ["All"]
        parties = ["All"]

        if not df.empty:
            districts += sorted(df["District"].dropna().unique().tolist())
            constituencies += sorted(df["Constituency"].unique().tolist())
            parties += sorted(df["Party"].unique().tolist())

        # 🎯 Filters
        selected_district = st.sidebar.selectbox("District", districts)
        selected_constituency = st.sidebar.selectbox("Constituency", constituencies)
        selected_party = st.sidebar.selectbox("Party", parties)

        # Apply filters
        filtered_df = df.copy()

        if selected_district != "All":
            filtered_df = filtered_df[
                filtered_df["District"] == selected_district
            ]

        if selected_constituency != "All":
            filtered_df = filtered_df[
                filtered_df["Constituency"] == selected_constituency
            ]

        if selected_party != "All":
            filtered_df = filtered_df[
                filtered_df["Party"] == selected_party
            ]

        with placeholder.container():

            st.caption(f"⏱️ Last Updated: {time.strftime('%H:%M:%S')}")

            # 📊 MAIN TABLE
            st.subheader("📊 Constituency-wise Live Results")
            st.dataframe(filtered_df, use_container_width=True)

            # 🏆 WINNERS
            if not winners.empty:
                st.subheader("🏆 Leading Candidates (Constituency)")
                st.dataframe(winners, use_container_width=True)

            # 📺 SEAT COUNT (TV STYLE)
            if not seat_count.empty:
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
                district_leaders = df.loc[
                    df.groupby("District")["Votes"].idxmax()
                ]
                st.dataframe(district_leaders)

            # 📊 PARTY VS CONSTITUENCY TABLE
            st.subheader("📊 Party-wise Votes per Constituency")

            pivot = df.pivot_table(
                index="Constituency",
                columns="Party",
                values="Votes",
                aggfunc="sum"
            ).fillna(0)

            st.dataframe(pivot, use_container_width=True)

            # 🧑‍💼 CANDIDATE CARDS
            if not winners.empty:
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

    time.sleep(10)
    st.rerun()