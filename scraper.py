import requests
import pandas as pd

NDTV_URL = "https://edata.ndtv.com/feeds/assembly/keralam/2026/json/WinnerCandidates_VS_KER.json"

def fallback():
    return pd.DataFrame([
        {
            "Constituency": "Fallback Seat",
            "Candidate": "Fallback Candidate",
            "Party": "LDF",
            "Votes": 1000,
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
            timeout=8
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text[:300])

        if response.status_code != 200:
            return fallback()

        data = response.json()

        print("TYPE:", type(data))

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

        return df

    except Exception as e:
        print("ERROR:", e)
        return fallback()
