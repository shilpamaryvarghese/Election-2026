import requests
import pandas as pd

URL = "https://data.ndtv.com/elections/2026/WinnerCandidates_VS_KER.json"

def fetch_ndtv_results():
    try:
        res = requests.get(URL, timeout=10)
        data = res.json()

        results = []

        for item in data:
            constituency = item.get("constituency_name")
            candidate = item.get("candidate_name")
            party = item.get("party_name")
            status = item.get("status")  # Leading / Won

            results.append({
                "Constituency": constituency,
                "Candidate": candidate,
                "Party": party,
                "Status": status
            })

        df = pd.DataFrame(results)
        return df

    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_ndtv_results()
    print(df.head())
