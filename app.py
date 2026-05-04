from flask import Flask, render_template, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"

RESULT_API = "https://api.opendatakerala.org/api/kla2026/results/all.json"
HIT_API = "https://api.opendatakerala.org/api/kla2026/hitcounter"

CACHE = None
CACHE_TIME = 0
CACHE_EXPIRY = 30


# ---------------- LOAD CSV ----------------
def load_csv():
    try:
        df = pd.read_csv(CSV_FILE)

        df["Candidate_Name"] = df["Candidate_Name"].astype(str).str.strip().str.lower()
        df["Party"] = df["Party"].astype(str).str.strip().str.lower()
        df["Constituency_Name"] = df["Constituency_Name"].astype(str).str.strip()

        return df

    except Exception as e:
        print("CSV Error:", e)
        return pd.DataFrame()


# ---------------- FETCH API ----------------
def fetch_data():
    try:
        res = requests.get(RESULT_API, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except Exception as e:
        print("API Error:", e)
        return None


# ---------------- CACHE ----------------
def get_data():
    global CACHE, CACHE_TIME
    now = time.time()

    if CACHE and (now - CACHE_TIME < CACHE_EXPIRY):
        return CACHE

    data = fetch_data()

    if data:
        CACHE = data
        CACHE_TIME = now

    return data


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- API: PARTY SUMMARY ----------------
@app.route("/api/overall-summary")
def overall_summary():
    data = get_data()

    if not data:
        return jsonify({"data": {}})

    df = pd.DataFrame(data)

    # CLEAN
    df["party"] = df["party"].str.upper()
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0)

    # PARTY → ALLIANCE
    alliance_map = {
        "INC": "UDF",
        "IUML": "UDF",

        "CPIM": "LDF",
        "CPI": "LDF",

        "BJP": "NDA"
    }

    df["Alliance"] = df["party"].map(alliance_map).fillna("Others")

    # TOTAL VOTES
    total_votes = int(df["votes"].sum())

    # GROUP
    summary = df.groupby("Alliance").agg(
        Seats=("status", lambda x: (x.str.lower() == "won").sum()),
        Votes=("votes", "sum")
    ).reset_index()

    # CALCULATE %
    summary["Percent"] = ((summary["Votes"] / total_votes) * 100).round(1)

    result = {
        "TotalSeats": 140,
        "TotalVotes": total_votes,
        "alliances": summary.to_dict(orient="records")
    }

    return jsonify({"data": result})


# ---------------- API: CONSTITUENCY ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    csv_df = load_csv()
    api_data = get_data()

    csv_df = csv_df[csv_df["Constituency_Name"].str.lower() == name.lower()]

    if not api_data:
        csv_df["Votes"] = 0
        csv_df["Status"] = "Dummy"

        return jsonify({"data": csv_df.to_dict(orient="records")})

    api_df = pd.DataFrame(api_data)

    api_df["candidate"] = api_df["candidate"].str.lower()
    api_df["party"] = api_df["party"].str.lower()
    api_df["constituency"] = api_df["constituency"].str.strip()

    api_df = api_df[api_df["constituency"].str.lower() == name.lower()]

    merged = pd.merge(
        csv_df,
        api_df,
        left_on=["Candidate_Name", "Party"],
        right_on=["candidate", "party"],
        how="left"
    )

    merged["Votes"] = merged["votes"].fillna(0)
    merged["Status"] = merged["status"].fillna("NA")

    return jsonify({"data": merged.to_dict(orient="records")})


# ---------------- API: CONSTITUENCIES ----------------
@app.route("/api/constituencies")
def get_constituencies():
    df = load_csv()

    return jsonify({
        "data": sorted(df["Constituency_Name"].unique())
    })


# ---------------- API: HIT COUNTER ----------------
@app.route("/api/hitcount")
def hitcount():
    try:
        res = requests.get(HIT_API, timeout=5)
        return jsonify(res.json())
    except:
        return jsonify({"count": 0})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
