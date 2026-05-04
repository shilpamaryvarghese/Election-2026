import requests
import pandas as pd

API_URL = "https://data.ndtv.com/elections/2026/kerala.json"

def fetch_ndtv_data():
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()

        results = []

        for item in data.get("data", []):
            constituency = item.get("constituency")
            candidate = item.get("candidate")
            party = item.get("party")
            status = item.get("status")

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
    df = fetch_ndtv_data()
    print(df.head())
