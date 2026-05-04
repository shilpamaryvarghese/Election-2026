import streamlit as st
import pandas as pd
import time

from scraper import fetch_data

st.set_page_config(
    page_title="Kerala Election Live",
    layout="wide"
)

st.title("🗳️ Kerala Election 2026 - Live Dashboard")

st.markdown(
    "<meta http-equiv='refresh' content='30'>",
    unsafe_allow_html=True
)

df = fetch_data()

df["Votes"] = pd.to_numeric(
    df["Votes"],
    errors="coerce"
).fillna(0)

winners = (
    df.sort_values("Votes", ascending=False)
      .drop_duplicates("Constituency")
)

seat_count = winners["Party"].value_counts()

st.caption(
    f"Last updated: {time.strftime('%H:%M:%S')}"
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Constituency Results")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("Party Seat Count")
    st.bar_chart(seat_count)

st.subheader("Leading Candidates")
st.dataframe(winners, use_container_width=True)

st.subheader("Total Votes by Party")
party_votes = df.groupby("Party")["Votes"].sum()
st.bar_chart(party_votes)
