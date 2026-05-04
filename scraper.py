import pandas as pd
import requests

URL = "https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S11.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_party_data():
    res = requests.get(URL, headers=HEADERS, timeout=10)
    tables = pd.read_html(res.text)

    df = tables[0]

    df.columns = ["Party", "Won", "Leading", "Total"]

    df = df[df["Party"].notna()]

    df["Won"] = pd.to_numeric(df["Won"], errors="coerce").fillna(0)
    df["Leading"] = pd.to_numeric(df["Leading"], errors="coerce").fillna(0)
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    return df
