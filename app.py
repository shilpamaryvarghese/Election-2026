from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

# =========================
# API URL
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
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# =========================
# CONSTITUENCY PAGE
# =========================
@app.route("/constituency")
def constituency():
    return render_template("constituency.html")


# =========================
# PARTYWISE PAGE
# =========================
@app.route("/partywise")
def partywise():
    return render_template("partywise.html")


# =========================
# CANDIDATES PAGE
# =========================
@app.route("/candidates")
def candidates():
    return render_template("candidates.html")


# =========================
# RESULTS API
# =========================
@app.route("/api/results")
def results():

    data = fetch_data()

    output = []

    for r in data:

        constituency = str(
            r.get("constituency", "")
        )

        output.append({

            "Constituency": constituency,

            "ConstNo": r.get(
                "constituency_number", ""
            ),

            "Candidate": r.get(
                "candidate", ""
            ),

            "Party": r.get(
                "party", ""
            ),

            "Alliance": r.get(
                "alliance", ""
            ),

            "Votes": int(
                r.get("votes", 0)
            ),

            "Percent": float(
                r.get("percentage", 0)
            ),

            "Status": r.get(
                "status", ""
            ),

            "Margin": int(
                r.get("margin", 0)
            ),

            "District": r.get(
                "district", ""
            )

        })

    return jsonify({
        "success": True,
        "count": len(output),
        "data": output
    })


# =========================
# CONSTITUENCY API
# =========================
@app.route("/api/constituency/<name>")
def constituency_data(name):

    data = fetch_data()

    filtered = []

    for r in data:

        constituency = str(
            r.get("constituency", "")
        )

        if constituency.lower() == name.lower():

            filtered.append({

                "Constituency": constituency,

                "Candidate": r.get(
                    "candidate", ""
                ),

                "Party": r.get(
                    "party", ""
                ),

                "Votes": int(
                    r.get("votes", 0)
                ),

                "Percent": float(
                    r.get("percentage", 0)
                ),

                "Status": r.get(
                    "status", ""
                )

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

        party = str(
            r.get("party", "Unknown")
        )

        votes = int(
            r.get("votes", 0)
        )

        status = str(
            r.get("status", "")
        ).lower()

        if party not in parties:

            parties[party] = {

                "Party": party,

                "Seats": 0,

                "Votes": 0

            }

        if (
            "won" in status
            or
            "lead" in status
        ):

            parties[party]["Seats"] += 1

        parties[party]["Votes"] += votes

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

            "Candidate": r.get(
                "candidate", ""
            ),

            "Party": r.get(
                "party", ""
            ),

            "Constituency": str(
                r.get("constituency", "")
            ),

            "Votes": int(
                r.get("votes", 0)
            ),

            "Percent": float(
                r.get("percentage", 0)
            ),

            "Status": r.get(
                "status", ""
            )

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
