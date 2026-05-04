import pandas as pd
import requests

MAIN_API = "https://edata.ndtv.com/feeds/elex/2026/electionswidget2026.json"
WINNER_API = "https://edata.ndtv.com/feeds/assembly/keralam/2026/json/WinnerCandidates_VS_KER.json"

def fetch_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        main_res = requests.get(MAIN_API, headers=headers).json()
        winner_res = requests.get(WINNER_API, headers=headers).json()

        main_data = main_res.get("data", main_res)
        winner_data = winner_res.get("data", winner_res)

        winner_map = {}
        for w in winner_data:
            constituency = w.get("constituency") or w.get("seat")
            winner_map[constituency] = {
                "Candidate": w.get("candidate"),
                "Party": w.get("party")
            }

        records = []

        for item in main_data:
            constituency = item.get("constituency") or item.get("seat")

            records.append({
                "Constituency": constituency,
                "Candidate": winner_map.get(constituency, {}).get("Candidate", "N/A"),
                "Party": winner_map.get(constituency, {}).get("Party", "N/A"),
                "Votes": item.get("votes") or item.get("total_votes", 0)
            })

        df = pd.DataFrame(records)
        df["Constituency"] = df["Constituency"].astype(str).str.strip()

        return df

    except:
        return pd.DataFrame()
