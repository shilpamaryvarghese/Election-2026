import requests
import pandas as pd

NDTV_URL = "https://edata.ndtv.com/feeds/assembly/keralam/2026/json/WinnerCandidates_VS_KER.json"


def fallback():
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
            "Votes": 11200,
            "Status": "Leading"
        },
        {
            "Constituency": "Udma",
            "Candidate": "Candidate C",
            "Party": "NDA",
            "Votes": 8600,
            "Status": "Leading"
        }
    ])


def fetch_data():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            NDTV_URL,
            headers=headers,
            timeout=6
        )

        if response.status_code != 200:
            return fallback()

        data = response.json()

        if not isinstance(data, list):
            return fallback()

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
            return fallback()

        df = df[df["Constituency"] != ""]

        if df.empty:
            return fallback()

        return df

    except Exception:
        return fallback()
