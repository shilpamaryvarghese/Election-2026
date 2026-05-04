import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://results.eci.gov.in/ResultAcGenMay2026/election-json-S11-live.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_data():
    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.find_all("tr")

        data = []
        for row in rows:
            cols = [c.text.strip() for c in row.find_all("td")]
            if len(cols) >= 4:
                data.append(cols[:4])

        df = pd.DataFrame(data, columns=[
            "Constituency", "Candidate", "Party", "Votes"
        ])

        df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

        df = df.dropna(subset=["Constituency", "Party"])

        df["Constituency"] = df["Constituency"].astype(str).str.strip()
        df["Candidate"] = df["Candidate"].astype(str).str.strip()
        df["Party"] = df["Party"].astype(str).str.strip()

        return df

    except:
        return pd.DataFrame()
