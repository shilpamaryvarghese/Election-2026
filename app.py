from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/"

# ---------------- CACHE ----------------
CACHE = {}
CACHE_TIME = {}
CACHE_EXPIRY = 30


# ---------------- LOAD CSV ----------------
def load_data():
    df = pd.read_csv(CSV_FILE)

    df["Candidate_Name"] = df["Candidate_Name"].astype(str).str.strip().str.lower()
    df["Party"] = df["Party"].astype(str).str.strip().str.lower()
    df["Constituency_Name"] = df["Constituency_Name"].astype(str).str.strip()

    return df


# ---------------- GET LINKS ----------------
def get_constituency_links():
    try:
        url = BASE_URL + "index.htm"

        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = {}

        for a in soup.find_all("a"):
            name = a.text.strip()
            href = a.get("href")

            if href and "S11" in href and ".htm" in href:
                links[name] = href

        return links

    except Exception as e:
        print("Link error:", e)
        return {}


# ---------------- FETCH DATA ----------------
def fetch_constituency_data(name):
    try:
        print("Fetching:", name)

        links = get_constituency_links()
        page = links.get(name)

        if not page:
            return None

        url = BASE_URL + page

        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")

        data = []

        for row in table.find_all("tr")[1:]:
            cols = [c.text.strip() for c in row.find_all("td")]

            if len(cols) >= 4:
                data.append({
                    "Candidate_Name": cols[0].lower(),
                    "Party": cols[1].lower(),
                    "Votes": cols[2],
                    "Status": cols[3]
                })

        return data

    except Exception as e:
        print("Fetch error:", e)
        return None


# ---------------- CACHE ----------------
def get_cached_data(name):
    now = time.time()

    if name in CACHE and (now - CACHE_TIME[name] < CACHE_EXPIRY):
        return CACHE[name]

    data = fetch_constituency_data(name)

    CACHE[name] = data
    CACHE_TIME[name] = now

    return data


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/constituency/<name>")
def constituency_page(name):
    return render_template("constituency.html", name=name)


# ---------------- API: CONSTITUENCY ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    df = load_data()
    df = df[df["Constituency_Name"] == name]

    live_data = get_cached_data(name)

    if live_data:
        live_df = pd.DataFrame(live_data)

        live_df["Candidate_Name"] = live_df["Candidate_Name"].str.strip().str.lower()
        live_df["Party"] = live_df["Party"].str.strip().str.lower()

        merged = pd.merge(df, live_df, on=["Candidate_Name", "Party"], how="left")

        merged["Votes"] = merged["Votes"].fillna("0")
        merged["Status"] = merged["Status"].fillna("NA")

        return jsonify({
            "dummy": False,
            "data": merged.to_dict(orient="records")
        })

    else:
        df["Votes"] = "0"
        df["Status"] = "Dummy"

        return jsonify({
            "dummy": True,
            "data": df.to_dict(orient="records")
        })


# ---------------- API: PARTY SUMMARY ----------------
@app.route("/api/party-summary")
def party_summary():
    df = load_data()

    all_data = []
    constituencies = df["Constituency_Name"].unique()

    for c in constituencies:
        live = get_cached_data(c)
        if live:
            all_data.extend(live)

    # ✅ IF LIVE DATA EXISTS
    if len(all_data) > 0:
        live_df = pd.DataFrame(all_data)

        live_df["Party"] = live_df["Party"].astype(str).str.strip().str.upper()
        live_df["Status"] = live_df["Status"].astype(str).str.lower()

        summary = live_df.groupby("Party").agg(
            Won=("Status", lambda x: (x == "won").sum()),
            Leading=("Status", lambda x: (x == "leading").sum())
        ).reset_index()

        summary["Total"] = summary["Won"] + summary["Leading"]

        return jsonify({
            "dummy": False,
            "data": summary.to_dict(orient="records")
        })

    # ✅ FALLBACK (NO BLANK PAGE)
    else:
        df["Party"] = df["Party"].str.upper()

        summary = df.groupby("Party").size().reset_index(name="Total")
        summary["Won"] = 0
        summary["Leading"] = 0

        return jsonify({
            "dummy": True,
            "data": summary.to_dict(orient="records")
        })


# ---------------- API: CONSTITUENCIES ----------------
@app.route("/api/constituencies")
def get_constituencies():
    df = load_data()

    return jsonify({
        "data": sorted(df["Constituency_Name"].unique())
    })


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
