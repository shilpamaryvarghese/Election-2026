from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/"
STATE_URL = BASE_URL + "statewiseS111.htm"

CACHE = {"data": None, "time": 0}
CACHE_EXPIRY = 60


# ================= FETCH ALL =================
def fetch_all():

    if time.time() - CACHE["time"] < CACHE_EXPIRY:
        return CACHE["data"]

    res = requests.get(STATE_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    links = {}
    for a in soup.find_all("a"):
        name = a.text.strip()
        href = a.get("href")
        if href and "Constituencywise" in href:
            links[name] = BASE_URL + href

    all_data = []

    for name, url in links.items():
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            s = BeautifulSoup(r.text, "html.parser")
            table = s.find("table")

            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")

                if len(cols) >= 6:
                    all_data.append({
                        "Constituency": name,
                        "Candidate": cols[0].text.strip(),
                        "Party": cols[1].text.strip(),
                        "Total": int(cols[4].text.strip().replace(",", "")),
                        "Percent": float(cols[5].text.strip().replace("%","") or 0)
                    })

        except:
            continue

    CACHE["data"] = all_data
    CACHE["time"] = time.time()

    return all_data


# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/partywise")
def partywise():
    return render_template("partywise.html")


#========================================
@app.route("/api/summary")
def summary():
    try:
        url = "https://results.eci.gov.in/ResultAcGenMay2026/election-json-S11-live.json"

        res = requests.get(url, timeout=10)
        data = res.json()

        parties = data.get("partywise", [])

        result = {
            "UDF": {"Seats": 0, "Votes": 0},
            "LDF": {"Seats": 0, "Votes": 0},
            "NDA": {"Seats": 0, "Votes": 0},
            "Others": {"Seats": 0, "Votes": 0}
        }

        # 🔥 PARTY → ALLIANCE MAP
        udf = ["INC","IUML","RSP","KER"]
        ldf = ["CPM","CPI"]
        nda = ["BJP","BDJS"]

        for p in parties:
            party = p.get("partyAbbr","").upper()
            seats = int(p.get("won",0)) + int(p.get("leading",0))
            votes = int(p.get("votes",0))

            if party in udf:
                result["UDF"]["Seats"] += seats
                result["UDF"]["Votes"] += votes

            elif party in ldf:
                result["LDF"]["Seats"] += seats
                result["LDF"]["Votes"] += votes

            elif party in nda:
                result["NDA"]["Seats"] += seats
                result["NDA"]["Votes"] += votes

            else:
                result["Others"]["Seats"] += seats
                result["Others"]["Votes"] += votes

        return jsonify({
            "data": [
                {"Alliance":k, "Seats":v["Seats"], "Votes":v["Votes"]}
                for k,v in result.items()
            ]
        })

    except Exception as e:
        print("Summary error:", e)

        return jsonify({
            "data":[
                {"Alliance":"UDF","Seats":0,"Votes":0},
                {"Alliance":"LDF","Seats":0,"Votes":0},
                {"Alliance":"NDA","Seats":0,"Votes":0},
                {"Alliance":"Others","Seats":0,"Votes":0}
            ]
        })

# ================= API =================

@app.route("/api/results")
def results():
    return jsonify({"data": fetch_all()})


@app.route("/api/partywise")
def partywise_api():

    data = fetch_all()

    party_map = {}

    for d in data:

        party = d["Party"]

        if party not in party_map:
            party_map[party] = {"votes": 0, "seats": 0}

        party_map[party]["votes"] += d["Total"]

    # winner = max votes per constituency
    winners = {}
    for d in data:
        c = d["Constituency"]
        if c not in winners or d["Total"] > winners[c]["Total"]:
            winners[c] = d

    for w in winners.values():
        party_map[w["Party"]]["seats"] += 1

    result = []
    for p, v in party_map.items():
        result.append({
            "party": p,
            "votes": v["votes"],
            "seats": v["seats"]
        })

    return jsonify({"data": result})


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
