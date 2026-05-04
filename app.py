from flask import Flask, jsonify
import requests

app = Flask(__name__)

# ✅ ONLY 2026 API
BASE_URL = "https://api.opendatakerala.org/api/lsg2026"


# =========================
# FETCH FUNCTION
# =========================
def fetch_api(endpoint):
    try:
        url = f"{BASE_URL}/{endpoint}"
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            return res.json()

        print("API Error:", res.status_code)
        return {}

    except Exception as e:
        print("Fetch Error:", e)
        return {}


# =========================
# RESULTS (USED EVERYWHERE)
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
# SUMMARY (INDEX PAGE)
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
# PARTYWISE
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
# CONSTITUENCY FILTER
# =========================
@app.route("/api/constituency/<name>")
def constituency(name):

    data = fetch_api("constituency")

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
