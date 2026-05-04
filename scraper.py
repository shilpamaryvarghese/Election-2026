import pandas as pd
import requests
from bs4 import BeautifulSoup
import random

URL = "https://results.eci.gov.in/"

def fetch_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        page = requests.get(URL, headers=headers, timeout=10)

        soup = BeautifulSoup(page.text, "html.parser")

        rows = soup.find_all("tr")

        data = []
        for row in rows:
            cols = [c.text.strip() for c in row.find_all("td")]
            if len(cols) >= 4:
                data.append(cols[:4])

        if not data:
            raise Exception("No data found")

        df = pd.DataFrame(data, columns=[
            "Constituency", "Candidate", "Party", "Votes"
        ])

        return df

    except Exception:
        # fallback dummy data
        constituencies = [f"Seat {i}" for i in range(1, 141)]
        parties = ["LDF", "UDF", "NDA", "Others"]

        df = pd.DataFrame({
            "Constituency": constituencies,
            "Candidate": ["Candidate"] * 140,
            "Party": [random.choice(parties) for _ in range(140)],
            "Votes": [random.randint(1000, 50000) for _ in range(140)]
        })

        return df
