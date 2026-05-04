from flask import Flask, render_template, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

# ---------------- API LINKS ----------------
RESULT_API = "https://api.opendatakerala.org/api/kla2026/results/all.json"
HIT_API = "https://api.opendatakerala.org/api/kla2026/hitcounter"

# ---------------- CACHE ----------------
CACHE = None
CACHE_TIME = 0
CACHE_EXPIRY = 30  # seconds


# ---------------- FETCH RESULT DATA ----------------
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

    # ⚠️ Adjust if API fields differ
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
    data = get_data()

    if not data:
        return jsonify({"dummy": True, "data": []})

    df = pd.DataFrame(data)

    # ⚠️ Adjust field name if needed
    df["constituency"] = df["constituency"].astype(str).str.strip()

    result = df[df["constituency"].str.lower() == name.lower()]

    return jsonify({
        "dummy": False,
        "data": result.to_dict(orient="records")
    })


# ---------------- API: CONSTITUENCIES LIST ----------------
@app.route("/api/constituencies")
def get_constituencies():
    try:
        df = pd.read_csv("kerala_2026_candidates.csv")

        df["Constituency_Name"] = df["Constituency_Name"].astype(str).str.strip()

        constituencies = sorted(df["Constituency_Name"].dropna().unique())

        return jsonify({
            "data": constituencies
        })

    except Exception as e:
        print("CSV Error:", e)
        return jsonify({"data": []})


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
