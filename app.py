from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

# =========================
# OPEN DATA KERALA API
# =========================
API_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"


# =========================
# FETCH DATA
# =========================
def fetch_data():
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("data", [])

        return []

    except Exception as e:
        print("API ERROR:", e)
        return []


# =========================
# PAGE ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/constituency")
def constituency():
    return render_template("constituency.html")


@app.route("/partywise")
def partywise():
    return render_template("partywise.html")


@app.route("/candidates")
def candidates():
    return render_template("candidates.html")


# =========================
# MAIN RESULTS API
# =========================
@app.route("/api/results")
def results():

    data = fetch_data()

    output = []

    for r in data:

        output.append({
            "Constituency": r.get("constituency", ""),
            "ConstNo": r.get("constituency_number", ""),
            "Candidate": r.get("candidate", ""),
            "Party": r.get("party", ""),
            "Alliance": r.get("alliance", ""),
            "Votes": r.get("votes", 0),
            "Percent": r.get("percentage", 0),
            "Status": r.get("status", ""),
            "Margin": r.get("margin", 0),
            "District": r.get("district", "")
        })

    return jsonify({
        "success": True,
        "count": len(output),
        "data": output
    })


# =========================
# SINGLE CONSTITUENCY API
# =========================
@app.route("/api/constituency/<name>")
def constituency_data(name):

    data = fetch_data()

    filtered = []

    for r in data:

        constituency = r.get("constituency", "")

        if constituency.lower() == name.lower():

            filtered.append({
                "Constituency": constituency,
                "ConstNo": r.get("constituency_number", ""),
                "Candidate": r.get("candidate", ""),
                "Party": r.get("party", ""),
                "Alliance": r.get("alliance", ""),
                "Votes": r.get("votes", 0),
                "Percent": r.get("percentage", 0),
                "Status": r.get("status", ""),
                "Margin": r.get("margin", 0),
                "District": r.get("district", "")
            })

    return jsonify({
        "success": True,
        "count": len(filtered),
        "data": filtered
    })


# =========================
# PARTYWISE API
# =========================
@app.route("/api/partywise")
def partywise_data():

    data = fetch_data()

    parties = {}

    for r in data:

        party = r.get("party", "Unknown")

        if party not in parties:
            parties[party] = {
                "Party": party,
                "Seats": 0,
                "Votes": 0
            }

        status = str(r.get("status", "")).lower()

        if "won" in status or "lead" in status:
            parties[party]["Seats"] += 1

        parties[party]["Votes"] += int(r.get("votes", 0))

    return jsonify({
        "success": True,
        "data": list(parties.values())
    })


# =========================
# CANDIDATES API
# =========================
@app.route("/api/candidates")
def candidates_api():

    data = fetch_data()

    candidates = []

    for r in data:

        candidates.append({
            "Candidate": r.get("candidate", ""),
            "Party": r.get("party", ""),
            "Constituency": r.get("constituency", ""),
            "Votes": r.get("votes", 0),
            "Status": r.get("status", "")
        })

    return jsonify({
        "success": True,
        "count": len(candidates),
        "data": candidates
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
