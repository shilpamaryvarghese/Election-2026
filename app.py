from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/"


# ---------------- LOAD CSV ----------------
def load_data():
    return pd.read_csv(CSV_FILE)


# ---------------- GET ALL CONSTITUENCY LINKS ----------------
def get_constituency_links():
    try:
        url = BASE_URL + "index.htm"
        res = requests.get(url, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")

        links = {}

        for a in soup.find_all("a"):
            text = a.text.strip()
            href = a.get("href")

            if href and "S11" in href and ".htm" in href:
                links[text] = href

        return links

    except Exception as e:
        print("Error fetching links:", e)
        return {}


# ---------------- FETCH CONSTITUENCY DATA ----------------
def fetch_constituency_data(constituency_name):
    try:
        links = get_constituency_links()

        page = links.get(constituency_name)

        if not page:
            return None

        url = BASE_URL + page

        res = requests.get(url, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")

        data = []

        for row in table.find_all("tr")[1:]:
            cols = [c.text.strip() for c in row.find_all("td")]

            if len(cols) >= 4:
                data.append({
                    "Candidate_Name": cols[0],
                    "Party": cols[1],
                    "Votes": cols[2],
                    "Status": cols[3]
                })

        return data

    except Exception as e:
        print("Error fetching constituency:", e)
        return None


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


# ---------------- API ----------------
@app.route("/api/constituency/<name>")
def api_constituency(name):
    df = load_data()
    df = df[df["Constituency_Name"] == name]

    live_data = fetch_constituency_data(name)

    if live_data:
        live_df = pd.DataFrame(live_data)

        merged = pd.merge(
            df,
            live_df,
            on=["Candidate_Name", "Party"],
            how="left"
        )

        merged["Votes"] = merged["Votes"].fillna("0")
        merged["Status"] = merged["Status"].fillna("NA")

        return jsonify({
            "dummy": False,
            "data": merged.to_dict(orient="records")
        })

    else:
        df["Votes"] = "0"
        df["Status"] = "Dummy"

        return jsonify({
            "dummy": True,
            "data": df.to_dict(orient="records")
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
