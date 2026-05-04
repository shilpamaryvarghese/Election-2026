from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://www.ndtv.com/elections/kerala/results-2026")

time.sleep(5)

cards = driver.find_elements(By.CLASS_NAME, "candidate-card")

for card in cards:
    name = card.text
    print(name)

driver.quit()
