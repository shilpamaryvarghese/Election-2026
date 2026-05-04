import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://results.eci.gov.in/ResultAcGenMay2026/election-json-S11-live.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Find table
table = soup.find("table")

rows = []
for tr in table.find_all("tr")[1:]:
    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
    if cols:
        rows.append(cols)

# Convert to DataFrame
df = pd.DataFrame(rows, columns=["Party", "Won", "Leading", "Total"])

print(df)
