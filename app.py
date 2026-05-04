from flask import Flask, render_template, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

API_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"

CACHE = None
CACHE_TIME = 0
CACHE_EXPIRY = 30


# ---------------- FETCH API ----------------
def fetch_data():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except:
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


@app.route("/constituency/<name>")
def constituency(name):
    return render_template("constituency.html", name=name)


# ---------------- API: ALLIANCE ----------------
@app.route("/api/alliance")
def alliance():
    data = get_data()
    if not data:
        return jsonify({"data": []})

    df = pd.DataFrame(data)

    df["party"] = df["party"].str.upper()
    df["status"] = df["status"].str.lower()

    alliance_map = {
        "CPIM": "LDF",
        "CPI": "LDF",
        "INC": "UDF",
        "IUML": "UDF",
        "BJP": "NDA"
    }

    df["Alliance"] = df["party"].map(alliance_map).fillna("Others")

    summary = df.groupby("Alliance").agg(
        Won=("status", lambda x: (x == "won").sum()),
        Leading=("status", lambda x: (x == "leading").sum())
    ).reset_index()

    summary["Total"] = summary["Won"] + summary["Leading"]

    return jsonify({"data": summary.to_dict(orient="records")})


# ---------------- API: CONSTITUENCY ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    data = get_data()
    if not data:
        return jsonify({"data": []})

    df = pd.DataFrame(data)

    df["constituency"] = df["constituency"].str.strip()

    result = df[df["constituency"].str.lower() == name.lower()]

    return jsonify({"data": result.to_dict(orient="records")})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
