import requests
import pandas as pd

URL = "https://edata.ndtv.com/feeds/assembly/keralam/2026/json/WinnerCandidates_VS_KER.json"


def fallback_data():
    return pd.DataFrame([
        {
            "Constituency": "Manjeshwar",
            "Candidate": "Candidate A",
            "Party": "LDF",
            "Votes": 12000,
            "Status": "Leading"
        },
        {
            "Constituency": "Kasaragod",
            "Candidate": "Candidate B",
            "Party": "UDF",
            "Votes": 10800,
            "Status": "Leading"
        },
        {
            "Constituency": "Udma",
            "Candidate": "Candidate C",
            "Party": "NDA",
            "Votes": 9200,
            "Status": "Leading"
        }
    ])


def fetch_data():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(URL, headers=headers, timeout=8)

        if res.status_code != 200:
            return fallback_data()

        data = res.json()

        if not isinstance(data, list):
            return fallback_data()

        rows = []

        for item in data:
            rows.append({
                "Constituency": item.get("constituency_name", ""),
                "Candidate": item.get("candidate_name", ""),
                "Party": item.get("party_name", ""),
                "Votes": item.get("votes", 0),
                "Status": item.get("status", "")
            })

        df = pd.DataFrame(rows)

        if df.empty:
            return fallback_data()

        df = df[df["Constituency"] != ""]

        if df.empty:
            return fallback_data()

        return df

    except Exception:
        return fallback_data()
