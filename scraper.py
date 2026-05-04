import requests
import pandas as pd

URL = "https://edata.ndtv.com/feeds/assembly/keralam/2026/json/WinnerCandidates_VS_KER.json"

def fetch_data():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(URL, headers=headers, timeout=10)

        if res.status_code != 200:
            print("Failed to fetch:", res.status_code)
            return pd.DataFrame()

        data = res.json()

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
        df = df[df["Constituency"] != ""]

        return df

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
