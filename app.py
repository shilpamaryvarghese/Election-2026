import streamlit as st
import time

from scraper import fetch_data
from data_utils import process_data

try:
    from photos import get_candidate_photo
except Exception:
    def get_candidate_photo(name):
        return "https://via.placeholder.com/100"

st.set_page_config(layout="wide")
st.title("🗳️ Kerala Election 2026 - LIVE Dashboard")

# auto refresh every 60 sec
st.markdown(
    "<meta http-equiv='refresh' content='60'>",
    unsafe_allow_html=True
)

st.sidebar.header("Filters")

try:
    raw_df = fetch_data()

    if raw_df is None or raw_df.empty:
        st.warning("Waiting for election data...")
        st.stop()

    df, winners, seat_count = process_data(raw_df)

    constituency_options = ["All"] + sorted(df["Constituency"].unique().tolist())
    party_options = ["All"] + sorted(df["Party"].unique().tolist())

    selected_constituency = st.sidebar.selectbox(
        "Constituency", constituency_options
    )
    selected_party = st.sidebar.selectbox(
        "Party", party_options
    )

    filtered_df = df.copy()

    if selected_constituency != "All":
        filtered_df = filtered_df[
            filtered_df["Constituency"] == selected_constituency
        ]

    if selected_party != "All":
        filtered_df = filtered_df[
            filtered_df["Party"] == selected_party
        ]

    st.caption(f"Last Updated: {time.strftime('%H:%M:%S')}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Constituency Results")
        st.dataframe(filtered_df, use_container_width=True)

    with col2:
        st.subheader("Party Seat Count")
        st.bar_chart(seat_count)

    st.subheader("Leading Candidates")
    st.dataframe(winners, use_container_width=True)

    st.subheader("Total Votes by Party")
    party_votes = df.groupby("Party")["Votes"].sum()
    st.bar_chart(party_votes)

    st.subheader("Candidate Details")

    cols = st.columns(4)

    for i, row in winners.head(8).iterrows():
        with cols[i % 4]:
            img = get_candidate_photo(row["Candidate"])
            st.image(img, width=90)
            st.markdown(f"**{row['Candidate']}**")
            st.write(f"Party: {row['Party']}")
            st.write(f"Votes: {row['Votes']}")

except Exception as e:
    st.error(f"Error: {e}")
