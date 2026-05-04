from flask import Flask, jsonify, render_template
import requests
import time

app = Flask(__name__)

# 🔗 API LINKS
BASE_NEW = "https://api.opendatakerala.org/api/lsg2026"
BASE_OLD = "https://api.opendatakerala.org/api/lsg2025"

# 🔥 CACHE (prevents too many API calls)
CACHE = {"data": None, "time": 0}
CACHE_EXPIRY = 20


# =========================
# FETCH API (AUTO SWITCH)
# =========================
def fetch_api(endpoint):

    # ✅ use cache
    if time.time() - CACHE["time"] < CACHE_EXPIRY:
        return CACHE["data"]

    # 🔹 Try 2026
    try:
        url = f"{BASE_NEW}/{endpoint}"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            print("Using 2026 API")
            data = res.json()
            CACHE["data"] = data
            CACHE["time"] = time.time()
            return data
    except:
        pass

    # 🔹 Fallback 2025
    try:
        url = f"{BASE_OLD}/{endpoint}"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            print("Using 2025 API")
            data = res.json()
            CACHE["data"] = data
            CACHE["time"] = time.time()
            return data
    except:
        pass

    return {"data": []}


# =========================
# PAGE ROUTES (IMPORTANT)
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/constituency")
def constituency_page():
    return render_template("constituency.html")

@app.route("/partywise")
def partywise_page():
    return render_template("partywise.html")

@app.route("/candidates")
def candidates_page():
    return render_template("candidates.html")


# =========================
# API: RESULTS
# =========================
@app.route("/api/results")
def results():

    data = fetch_api("results/all.json")

    output = []

    for r in data.get("data", []):
        output.append({
            "Constituency": r.get("constituency",""),
            "Candidate": r.get("candidate",""),
            "Party": r.get("party",""),
            "Total": int(r.get("votes",0)),
            "Percent": r.get("percentage",0)
        })

    return jsonify({"data": output})


# =========================
# API: SUMMARY
# =========================
@app.route("/api/summary")
def summary():

    data = fetch_api("summary")

    result = []

    for r in data.get("data", []):
        result.append({
            "Alliance": r.get("alliance","Others"),
            "Seats": int(r.get("seats",0)),
            "Votes": int(r.get("votes",0))
        })

    return jsonify({"data": result})


# =========================
# API: PARTYWISE
# =========================
@app.route("/api/partywise")
def partywise():

    data = fetch_api("partywise")

    result = []

    for r in data.get("data", []):
        result.append({
            "party": r.get("party",""),
            "seats": int(r.get("seats",0)),
            "votes": int(r.get("votes",0))
        })

    return jsonify({"data": result})


# =========================
# API: CONSTITUENCY FILTER
# =========================
@app.route("/api/constituency/<name>")
def constituency(name):

    data = fetch_api("results/all.json")

    filtered = []

    for r in data.get("data", []):
        if r.get("constituency","").lower() == name.lower():
            filtered.append({
                "Candidate": r.get("candidate",""),
                "Party": r.get("party",""),
                "Total": int(r.get("votes",0)),
                "Percent": r.get("percentage",0)
            })

    return jsonify({"data": filtered})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
