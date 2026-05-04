from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# =========================
# ECI URL
# =========================
ECI_URL = "https://results.eci.gov.in/ResultAcGenMay2026/election-json-S11-live.json"

# =========================
# FETCH ECI DATA
# =========================
def fetch_eci_data():
    try:
        res = requests.get(ECI_URL, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")

        if not table:
            return []

        rows = table.find_all("tr")[1:]

        data = []

        for row in rows:
            cols = row.find_all("td")

            if len(cols) < 8:
                continue

            data.append({
                "Constituency": cols[0].text.strip(),
                "ConstNo": cols[1].text.strip(),
                "LeadingCandidate": cols[2].text.strip(),
                "LeadingParty": cols[3].text.strip(),
                "TrailingCandidate": cols[4].text.strip(),
                "TrailingParty": cols[5].text.strip(),
                "Margin": cols[6].text.strip(),
                "Status": cols[7].text.strip()
            })

        return data

    except Exception as e:
        print("ECI ERROR:", e)
        return []


# =========================
# FALLBACK API
# =========================
def fallback_data():
    try:
        url = "https://api.opendatakerala.org/api/lsg2025/results/all.json"
        res = requests.get(url)
        data = res.json()

        return data if isinstance(data, list) else data.get("data", [])
    except:
        return []


# =========================
# PAGE ROUTES
# =========================
@app.route("/summary")
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

    data = fetch_eci_data()

    # fallback if empty
    if not data:
        data = fallback_data()

    output = []

    for r in data:

        # If ECI format
        if "LeadingCandidate" in r:
            output.append({
                "Constituency": r["Constituency"],
                "Candidate": r["LeadingCandidate"],
                "Party": r["LeadingParty"],
                "Total": r["Margin"],
                "Percent": 0,
                "Status": r["Status"]
            })

        else:
            output.append({
                "Constituency": r.get("constituency",""),
                "Candidate": r.get("candidate",""),
                "Party": r.get("party",""),
                "Total": int(r.get("votes",0)),
                "Percent": float(r.get("percentage",0)),
                "Status": r.get("status","")
            })

    return jsonify({"data": output})


# =========================
# CONSTITUENCY API
# =========================
@app.route("/api/constituency/<name>")
def constituency_data(name):

    data = fetch_eci_data()

    if not data:
        data = fallback_data()

    filtered = []

    for r in data:

        cname = r.get("Constituency") or r.get("constituency")

        if cname and cname.lower() == name.lower():

            filtered.append({
                "Candidate": r.get("LeadingCandidate") or r.get("candidate"),
                "Party": r.get("LeadingParty") or r.get("party"),
                "Total": r.get("Margin") or r.get("votes"),
                "Status": r.get("Status") or r.get("status")
            })

    return jsonify({"data": filtered})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
