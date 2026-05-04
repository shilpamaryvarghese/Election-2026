import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_BASE = "https://api.opendatakerala.org/api/kla2026"

ALLIANCE_COLORS = {
    "LDF": "#C62828",
    "UDF": "#0077B6",
    "NDA": "#E65100",
    "others": "#6B7280",
}

PARTY_COLORS = {
    "Indian National Congress": "#0077B6",
    "Communist Party of India (Marxist)": "#C62828",
    "Communist Party of India": "#B71C1C",
    "Indian Union Muslim League": "#1B5E20",
    "Bharatiya Janata Party": "#E65100",
    "Kerala Congress (M)": "#7B1FA2",
    "Revolutionary Socialist Party": "#4A148C",
    "Janata Dal (Secular)": "#F57F17",
    "Nationalist Congress Party": "#006064",
    "Kerala Congress": "#E91E63",
    "Independent": "#546E7A",
}

_cache = {
    "data": None,
    "last_fetched": None,
    "raw_api": None,
}

def fetch_api_data():
    try:
        response = requests.get(f"{API_BASE}/results/all.json", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API fetch error: {e}")
        return None

def process_api_data(api_data):
    if not api_data or not api_data.get("data"):
        return None

    constituencies_raw = api_data["data"]
    total_seats = len(constituencies_raw)

    alliance_tally = {}
    party_tally = {}
    constituency_results = []

    for const_item in constituencies_raw:
        const_info = const_item.get("constituency", {})
        candidates_list = const_item.get("candidates", [])

        const_number = const_info.get("constituency_Number", "")
        const_name = const_info.get("constituency_Name", "")
        const_name_ml = const_info.get("constituency_Name_(Malayalam)", "")
        district = const_info.get("district", "")
        region = const_info.get("region", "")
        reservation = const_info.get("reservation", "")
        result_declared = const_info.get("resultDeclared", "NO")
        lead_won_status = const_info.get("leadWonStatus", "")
        total_rounds = const_info.get("roundlist", {}).get("total_rounds", 0)
        completed_rounds = const_info.get("roundlist", {}).get("completed_rounds", 0)
        polling_pct = const_info.get("Polling % (2026)", "")
        total_voters = const_info.get("Voters Total", "")

        sorted_cands = sorted(candidates_list, key=lambda x: x.get("votes", 0), reverse=True)

        leading = sorted_cands[0] if sorted_cands else None
        runner_up = sorted_cands[1] if len(sorted_cands) > 1 else None

        margin = 0
        if leading and runner_up:
            margin = leading.get("votes", 0) - runner_up.get("votes", 0)

        cand_details = []
        for i, cand in enumerate(sorted_cands):
            alliance = cand.get("alliance", "others")
            party_name = cand.get("party", "")
            cand_name = cand.get("name", "")
            cand_name_ml = cand.get("name_ml", "")
            votes = cand.get("votes", 0)

            cand_details.append({
                "position": i + 1,
                "name": cand_name,
                "name_ml": cand_name_ml,
                "party": party_name,
                "alliance": alliance,
                "votes": votes,
                "color": ALLIANCE_COLORS.get(alliance, PARTY_COLORS.get(party_name, "#6B7280")),
            })

        if leading:
            alliance = leading.get("alliance", "others")
            if alliance not in alliance_tally:
                alliance_tally[alliance] = {"won": 0, "leading": 0, "total": 0, "votes": 0}
            if result_declared == "YES":
                alliance_tally[alliance]["won"] += 1
            else:
                alliance_tally[alliance]["leading"] += 1
            alliance_tally[alliance]["total"] += 1
            alliance_tally[alliance]["votes"] += leading.get("votes", 0)

            party_key = leading.get("party", "Independent")
            if party_key not in party_tally:
                party_tally[party_key] = {"won": 0, "leading": 0, "total": 0, "votes": 0, "alliance": alliance}
            if result_declared == "YES":
                party_tally[party_key]["won"] += 1
            else:
                party_tally[party_key]["leading"] += 1
            party_tally[party_key]["total"] += 1
            party_tally[party_key]["votes"] += leading.get("votes", 0)

        constituency_results.append({
            "number": const_number,
            "name": const_name,
            "name_ml": const_name_ml,
            "district": district,
            "region": region,
            "reservation": reservation,
            "result_declared": result_declared,
            "lead_won_status": lead_won_status,
            "total_rounds": total_rounds,
            "completed_rounds": completed_rounds,
            "polling_pct": polling_pct,
            "total_voters": total_voters,
            "leading": {
                "name": leading.get("name", ""),
                "name_ml": leading.get("name_ml", ""),
                "party": leading.get("party", ""),
                "alliance": leading.get("alliance", "others"),
                "votes": leading.get("votes", 0),
                "color": ALLIANCE_COLORS.get(leading.get("alliance", "others"), "#6B7280"),
            } if leading else None,
            "runner_up": {
                "name": runner_up.get("name", ""),
                "party": runner_up.get("party", ""),
                "alliance": runner_up.get("alliance", "others"),
                "votes": runner_up.get("votes", 0),
            } if runner_up else None,
            "margin": margin,
            "candidates": cand_details,
        })

    sorted_party_tally = sorted(party_tally.items(), key=lambda x: x[1]["total"], reverse=True)
    sorted_alliance_tally = sorted(alliance_tally.items(), key=lambda x: x[1]["total"], reverse=True)

    declared = sum(1 for c in constituency_results if c["result_declared"] == "YES")
    counting = total_seats - declared

    return {
        "total_seats": total_seats,
        "declared": declared,
        "counting": counting,
        "majority_mark": 71,
        "alliance_tally": sorted_alliance_tally,
        "party_tally": sorted_party_tally,
        "constituency_results": constituency_results,
        "last_updated": datetime.now().isoformat(),
    }

def get_processed_data():
    now = datetime.now()
    if _cache["data"] and _cache["last_fetched"]:
        elapsed = (now - _cache["last_fetched"]).total_seconds()
        if elapsed < 55:
            return _cache["data"]

    api_data = fetch_api_data()
    if api_data:
        processed = process_api_data(api_data)
        if processed:
            _cache["data"] = processed
            _cache["last_fetched"] = now
            _cache["raw_api"] = api_data
            return processed

    return _cache["data"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    data = get_processed_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "No data available"}), 503

@app.route("/api/sync", methods=["POST"])
def sync_api():
    _cache["last_fetched"] = None
    data = get_processed_data()
    if data:
        return jsonify({
            "success": True,
            "message": f"Synced {data['total_seats']} constituencies, {data['declared']} declared",
            "total_seats": data["total_seats"],
            "declared": data["declared"],
        })
    return jsonify({"success": False, "error": "Failed to fetch from API"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
