from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/"
STATE_URL = BASE_URL + "statewiseS111.htm"

# 🔥 CACHE
CACHE = {"data": None, "time": 0}
CACHE_EXPIRY = 60   # seconds


# =========================
# LOAD CSV
# =========================
def load_csv():
    df = pd.read_csv(CSV_FILE)
    df["Constituency_Name"] = df["Constituency_Name"].str.strip()
    return df


# =========================
# GET LINKS
# =========================
def get_links():
    res = requests.get(STATE_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    links = {}

    for a in soup.find_all("a"):
        name = a.text.strip()
        href = a.get("href")

        if href and "Constituencywise" in href:
            links[name] = BASE_URL + href

    return links


# =========================
# FETCH ALL CANDIDATES
# =========================
def fetch_all():

    # 🔥 CACHE CHECK
    if time.time() - CACHE["time"] < CACHE_EXPIRY:
        return CACHE["data"]

    links = get_links()
    all_data = []

    for name, url in links.items():

        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            table = soup.find("table")

            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")

                if len(cols) >= 6:
                    all_data.append({
                        "Constituency": name,
                        "Candidate": cols[0].text.strip(),
                        "Party": cols[1].text.strip(),
                        "EVM": cols[2].text.strip(),
                        "Postal": cols[3].text.strip(),
                        "Total": cols[4].text.strip(),
                        "Percent": cols[5].text.strip()
                    })

        except Exception as e:
            print("Error:", name, e)

        time.sleep(0.1)

    # SAVE CACHE
    CACHE["data"] = all_data
    CACHE["time"] = time.time()

    return all_data


# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/results")
def results():
    try:
        data = fetch_all()
        return jsonify({"data": data})
    except Exception as e:
        print(e)
        return jsonify({"data": []})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
