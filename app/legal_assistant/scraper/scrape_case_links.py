from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

base_url = "https://www.supremecourt.uk/cases?cs=Judgment+given&p="
case_links = set()

# Setup
options = Options()
options.add_argument("--headless=new")  # try removing this if page keeps failing
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

for page_num in range(1, 4):  # test first 3 pages
    url = base_url + str(page_num)
    driver.get(url)
    print(f"[~] Loading page {page_num}...")

    try:
        # Wait up to 10 seconds for case links to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.case-name"))
        )
        print(f"[+] Page {page_num}: Case links loaded!")

        # Save screenshot
        driver.save_screenshot(f"page_{page_num}.png")

        # Collect links
        elements = driver.find_elements(By.CSS_SELECTOR, "a.case-name")
        for el in elements:
            href = el.get_attribute("href")
            if href:
                case_links.add(href)

    except Exception as e:
        print(f"[!] Failed to load case links on page {page_num}: {e}")
        driver.save_screenshot(f"page_{page_num}_error.png")
        break

driver.quit()

print("\n✅ Total unique cases collected:", len(case_links))
for link in case_links:
    print(link)
