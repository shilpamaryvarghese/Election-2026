from flask import Flask, jsonify, render_template
import requests
import json

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
        if isinstance(data, dict):
            return data.get("data", [])
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print("API ERROR:", e)
        return []


# =========================
# HOME & PAGES
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
# RESULTS API (Flattened)
# =========================
@app.route("/api/results")
def results():
    raw_data = fetch_data()
    output = []

    for constituency_obj in raw_data:
        const_info = constituency_obj.get("constituency", {})
        candidates = constituency_obj.get("candidates", [])
        
        const_name = const_info.get("constituency_Name", "Unknown")
        result_declared = const_info.get("resultDeclared", "").upper() == "YES"
        lead_won_status = const_info.get("leadWonStatus", "")

        for i, c in enumerate(candidates):
            # Determine status
            status = ""
            if i == 0: # First candidate is the leader/winner
                if result_declared:
                    status = "Won"
                else:
                    status = lead_won_status if lead_won_status else "Lead"

            output.append({
                "constituency": const_name,
                "candidate": c.get("name", ""),
                "party": c.get("party", ""),
                "alliance": c.get("alliance", ""),
                "votes": int(c.get("votes", 0)),
                "status": status,
                "photo": c.get("photo", ""),
                "sitting": c.get("sitting", ""),
                "name_ml": c.get("name_ml", "")
            })

    return jsonify({
        "success": True,
        "count": len(output),
        "data": output
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
