import streamlit as st
import plotly.express as px
from scraper import fetch_party_data

st.set_page_config(layout="wide")

st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    font-weight: bold;
}
.title {
    text-align:center;
    font-size:22px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>General Election to Assembly Constituencies: Trends & Results May-2026</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:blue'>Kerala (Total AC : 140)</div>", unsafe_allow_html=True)

df = fetch_party_data()

# 🎨 Party colors
colors = {
    "INC": "#2c98f0",
    "CPI(M)": "#ff1a1a",
    "IUML": "#006400",
    "CPI": "#e60000",
    "BJP": "#f58231",
}

# 🔥 TOP CARDS
cols = st.columns(len(df.head(8)))

for i, row in df.head(8).iterrows():
    party = row["Party"]
    total = int(row["Total"])
    color = colors.get(party, "#9b59b6")

    cols[i].markdown(f"""
        <div class="card" style="background:{color}">
            {party}<br><h2>{total}</h2>
        </div>
    """, unsafe_allow_html=True)

# 📊 MAIN GRID
left, right = st.columns([2,1])

# 📋 TABLE
with left:
    st.subheader("Party Wise Results")
    st.dataframe(df, use_container_width=True)

# 🗺️ MAP PLACEHOLDER
with right:
    st.subheader("Constituency Wise Results")
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4c/Kerala_location_map.svg")

# 📊 CHARTS
c1, c2 = st.columns(2)

with c1:
    st.subheader("Party Wise Results")
    fig1 = px.pie(df, values="Total", names="Party", hole=0.5)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Vote Share")
    fig2 = px.pie(df, values="Total", names="Party")
    st.plotly_chart(fig2, use_container_width=True)

# 🔘 BUTTON
st.markdown("""
<div style='text-align:center'>
    <button style='background:#2c7be5;color:white;padding:10px 30px;border:none;border-radius:5px'>
        All Constituencies at a glance >
    </button>
</div>
""", unsafe_allow_html=True)
