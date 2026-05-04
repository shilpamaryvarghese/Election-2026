import requests
import pandas as pd

URL = "https://data.ndtv.com/elections/2026/WinnerCandidates_VS_KER.json"

def fetch_data():
    try:
        res = requests.get(URL, timeout=10)
        data = res.json()

        rows = []

        for item in data:
            rows.append({
                "Constituency": item.get("constituency_name"),
                "Candidate": item.get("candidate_name"),
                "Party": item.get("party_name"),
                "Votes": item.get("votes", 0), 
                "Status": item.get("status", "Won")
            })

        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        print("Error fetching NDTV data:", e)
        return pd.DataFrame()
