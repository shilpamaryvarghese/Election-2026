from flask import Flask, render_template, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

# ---------------- FILE + API ----------------
CSV_FILE = "kerala_2026_candidates.csv"

RESULT_API = "https://api.opendatakerala.org/api/kla2026/results/all.json"
HIT_API = "https://api.opendatakerala.org/api/kla2026/hitcounter"

# ---------------- CACHE ----------------
CACHE = None
CACHE_TIME = 0
CACHE_EXPIRY = 30  # seconds


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


# ---------------- CACHE WRAPPER ----------------
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


@app.route("/constituency/<name>")
def constituency(name):
    return render_template("constituency.html", name=name)


# ---------------- API: PARTY SUMMARY ----------------
@app.route("/api/party-summary")
def party_summary():
    data = get_data()

    if not data:
        return jsonify({"dummy": True, "data": []})

    df = pd.DataFrame(data)

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


# ---------------- API: CONSTITUENCY (MERGE CSV + API) ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    csv_df = load_csv()
    api_data = get_data()

    # FILTER CSV
    csv_df = csv_df[csv_df["Constituency_Name"].str.lower() == name.lower()]

    if not api_data:
        # fallback dummy
        csv_df["Votes"] = 0
        csv_df["Status"] = "Dummy"

        return jsonify({
            "dummy": True,
            "data": csv_df.to_dict(orient="records")
        })

    api_df = pd.DataFrame(api_data)

    # CLEAN API DATA
    api_df["candidate"] = api_df["candidate"].astype(str).str.strip().str.lower()
    api_df["party"] = api_df["party"].astype(str).str.strip().str.lower()
    api_df["constituency"] = api_df["constituency"].astype(str).str.strip()

    api_df = api_df[api_df["constituency"].str.lower() == name.lower()]

    # MERGE
    merged = pd.merge(
        csv_df,
        api_df,
        left_on=["Candidate_Name", "Party"],
        right_on=["candidate", "party"],
        how="left"
    )

    merged["Votes"] = merged["votes"].fillna(0)
    merged["Status"] = merged["status"].fillna("NA")

    return jsonify({
        "dummy": False,
        "data": merged.to_dict(orient="records")
    })


# ---------------- API: CONSTITUENCIES (FROM CSV) ----------------
@app.route("/api/constituencies")
def get_constituencies():
    df = load_csv()

    if df.empty:
        return jsonify({"data": []})

    constituencies = sorted(df["Constituency_Name"].dropna().unique())

    return jsonify({"data": constituencies})


# ---------------- API: HIT COUNTER ----------------
@app.route("/api/hitcount")
def hitcount():
    try:
        res = requests.get(HIT_API, timeout=5)

        if res.status_code != 200:
            return jsonify({"count": 0})

        return jsonify(res.json())

    except Exception as e:
        print("Hit API Error:", e)
        return jsonify({"count": 0})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
