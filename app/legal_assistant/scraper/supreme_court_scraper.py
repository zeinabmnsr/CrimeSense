'''


import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.supremecourt.uk"
LISTING_URL = BASE_URL + "/cases?cs=Judgment+given&p="

def get_case_links(page):
    url = LISTING_URL + str(page)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    cases = soup.select(".content .case")
    case_links = []
    for case in cases:
        link_tag = case.find("a", href=True)
        if link_tag:
            link = BASE_URL + link_tag["href"]
            title = link_tag.get_text(strip=True)
            date = case.find("p").get_text(strip=True)
            case_links.append({
                "title": title,
                "url": link,
                "date": date
            })
    return case_links

def get_case_details(case):
    res = requests.get(case["url"])
    soup = BeautifulSoup(res.content, "html.parser")

    # Try to extract the case summary
    summary = ""
    try:
        summary_tag = soup.select_one(".main-content .column-one .content p")
        if summary_tag:
            summary = summary_tag.get_text(" ", strip=True)
    except:
        pass

    # Get judgment link (PDF or HTML)
    links = soup.select(".attachments a")
    judgment_links = [BASE_URL + a["href"] for a in links if a["href"].endswith((".pdf", ".html"))]

    return {
        "title": case["title"],
        "date": case["date"],
        "url": case["url"],
        "summary": summary,
        "judgment_links": judgment_links
    }

def scrape_all(max_pages=25):  # ~500 cases
    all_cases = []
    for page in range(1, max_pages + 1):
        print(f"📄 Scraping page {page}")
        links = get_case_links(page)
        for case in links:
            print(f"🔍 {case['title']}")
            details = get_case_details(case)
            all_cases.append(details)
            time.sleep(0.3)  # Respectful scraping
    return all_cases

def save_to_json(data, path="app/legal_assistant/data/supreme_court_cases.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    data = scrape_all(max_pages=25)
    save_to_json(data)
    print(f"✅ Saved {len(data)} Supreme Court cases to JSON.")

    '''