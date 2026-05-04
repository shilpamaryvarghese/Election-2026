from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"


# ---------------- LOAD DATA ----------------
def load_data():
    return pd.read_csv(CSV_FILE)


# ---------------- FETCH LIVE DATA ----------------
def fetch_party_data():
    try:
        url = "https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S11.htm"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")

        data = {}

        for row in table.find_all("tr")[1:]:
            cols = [c.text.strip() for c in row.find_all("td")]

            if len(cols) >= 4:
                data[cols[0]] = {
                    "won": int(cols[1]),
                    "leading": int(cols[2])
                }

        return data
    except:
        return None


# ---------------- MERGE ----------------
def merge(df, party_data):
    df["Status"] = "NA"

    if not party_data:
        return df, True

    for party, stats in party_data.items():
        if stats["won"] > 0:
            df.loc[df["Party"] == party, "Status"] = "Won"
        elif stats["leading"] > 0:
            df.loc[df["Party"] == party, "Status"] = "Leading"

    return df, False


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/candidates")
def candidates_page():
    return render_template("candidates.html")


@app.route("/partywise")
def partywise_page():
    return render_template("partywise.html")


@app.route("/constituency/<name>")
def constituency_page(name):
    return render_template("constituency.html", name=name)


# ---------------- APIs ----------------
@app.route("/api/candidates")
def api_candidates():
    df = load_data()
    party_data = fetch_party_data()

    df, dummy = merge(df, party_data)

    party = request.args.get("party")
    district = request.args.get("district")
    constituency = request.args.get("constituency")
    search = request.args.get("search")

    if party:
        df = df[df["Party"] == party]

    if district:
        df = df[df["District"] == district]

    if constituency:
        df = df[df["Constituency_Name"] == constituency]

    if search:
        df = df[df["Candidate_Name"].str.contains(search, case=False, na=False)]

    return jsonify({
        "dummy": dummy,
        "data": df.to_dict(orient="records"),
        "filters": {
            "party": sorted(df["Party"].dropna().unique().tolist()),
            "district": sorted(df["District"].dropna().unique().tolist()),
            "constituency": sorted(df["Constituency_Name"].dropna().unique().tolist())
        }
    })


@app.route("/api/partywise")
def api_partywise():
    df = load_data()
    party_data = fetch_party_data()

    summary = df.groupby("Party").size().reset_index(name="Candidates")

    if party_data:
        summary["Won"] = summary["Party"].map(lambda x: party_data.get(x, {}).get("won", 0))
        summary["Leading"] = summary["Party"].map(lambda x: party_data.get(x, {}).get("leading", 0))
        dummy = False
    else:
        summary["Won"] = 0
        summary["Leading"] = 0
        dummy = True

    return jsonify({
        "dummy": dummy,
        "data": summary.to_dict(orient="records")
    })


@app.route("/api/constituency/<name>")
def api_constituency(name):
    df = load_data()
    party_data = fetch_party_data()

    df, dummy = merge(df, party_data)
    df = df[df["Constituency_Name"] == name]

    return jsonify({
        "dummy": dummy,
        "data": df.to_dict(orient="records")
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
