from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)

def fetch_live_results():
    driver = get_driver()
    driver.get("https://results.eci.gov.in/")
    time.sleep(5)

    rows = driver.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cols = row.text.split("\n")
        if len(cols) >= 4:
            data.append(cols[:4])

    driver.quit()

    df = pd.DataFrame(data, columns=[
        "Constituency", "Candidate", "Party", "Votes"
    ])

    return df