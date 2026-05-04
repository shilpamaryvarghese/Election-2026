from flask import Flask, render_template, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
API_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"

# ---------------- CACHE ----------------
CACHE = None
CACHE_TIME = 0
CACHE_EXPIRY = 30  # seconds


# ---------------- LOAD CSV ----------------
def load_data():
    df = pd.read_csv(CSV_FILE)

    df["Candidate_Name"] = df["Candidate_Name"].astype(str).str.strip().str.lower()
    df["Party"] = df["Party"].astype(str).str.strip().str.lower()
    df["Constituency_Name"] = df["Constituency_Name"].astype(str).str.strip()

    return df


# ---------------- FETCH API DATA ----------------
def fetch_api_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(API_URL, headers=headers, timeout=10)

        if res.status_code != 200:
            return None

        return res.json()

    except Exception as e:
        print("API error:", e)
        return None


# ---------------- CACHE WRAPPER ----------------
def get_cached_data():
    global CACHE, CACHE_TIME

    now = time.time()

    if CACHE and (now - CACHE_TIME < CACHE_EXPIRY):
        return CACHE

    data = fetch_api_data()

    if data:
        CACHE = data
        CACHE_TIME = now

    return data


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/constituency/<name>")
def constituency_page(name):
    return render_template("constituency.html", name=name)


# ---------------- API: PARTY SUMMARY ----------------
@app.route("/api/party-summary")
def party_summary():
    data = get_cached_data()

    if not data:
        return jsonify({"dummy": True, "data": []})

    df = pd.DataFrame(data)

    # ⚠️ Adjust column names if needed
    df["party"] = df["party"].astype(str).str.upper()
    df["status"] = df["status"].astype(str).str.lower()

    summary = df.groupby("party").agg(
        Won=("status", lambda x: (x == "won").sum()),
        Leading=("status", lambda x: (x == "leading").sum())
    ).reset_index()

    summary["Total"] = summary["Won"] + summary["Leading"]

    return jsonify({
        "dummy": False,
        "data": summary.rename(columns={"party": "Party"}).to_dict(orient="records")
    })


# ---------------- API: CONSTITUENCY ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    data = get_cached_data()

    if not data:
        return jsonify({"dummy": True, "data": []})

    df = pd.DataFrame(data)

    # ⚠️ Adjust based on API fields
    df["constituency"] = df["constituency"].astype(str).str.strip()

    result = df[df["constituency"].str.lower() == name.lower()]

    if result.empty:
        return jsonify({"dummy": True, "data": []})

    return jsonify({
        "dummy": False,
        "data": result.to_dict(orient="records")
    })


# ---------------- API: CONSTITUENCIES ----------------
@app.route("/api/constituencies")
def get_constituencies():
    data = get_cached_data()

    if not data:
        return jsonify({"data": []})

    df = pd.DataFrame(data)

    return jsonify({
        "data": sorted(df["constituency"].dropna().unique())
    })


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
