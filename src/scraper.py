from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import time
import json
import os

BASE_URL = "https://debales.ai"
MAX_PAGES = 50
DELAY = 1500  # milliseconds between pages

SKIP_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".zip", ".svg", ".gif"]
SKIP_KEYWORDS = ["/login", "/signup", "/cart", "/checkout", "/cdn", "/static"]

def is_valid_url(url, base_domain):
    parsed = urlparse(url)
    # must be same domain
    if base_domain not in parsed.netloc:
        return False
    # skip files
    for ext in SKIP_EXTENSIONS:
        if url.endswith(ext):
            return False
    # skip unwanted pages
    for keyword in SKIP_KEYWORDS:
        if keyword in url:
            return False
    return True

def chunk_text(text, source_url, chunk_size=500, overlap=50):
    chunks = []
    text = text.strip()
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append({
                "text": chunk.strip(),
                "source": source_url
            })
        start = end - overlap
    return chunks

def scrape_site():
    visited = set()
    queue = [BASE_URL]
    all_chunks = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        base_domain = urlparse(BASE_URL).netloc

        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)

            if url in visited:
                continue

            print(f"Scraping: {url}")

            try:
                page.goto(url, timeout=15000)
                page.wait_for_timeout(DELAY)

                # scroll to bottom to load lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)

                # get all text
                text = page.inner_text("body")

                # chunk it
                chunks = chunk_text(text, url)
                all_chunks.extend(chunks)
                print(f"  → {len(chunks)} chunks extracted")

                # get all links
                links = page.eval_on_selector_all(
                    "a[href]",
                    "els => els.map(e => e.href)"
                )

                for link in links:
                    link = link.strip()
                    if link and is_valid_url(link, base_domain) and link not in visited:
                        queue.append(link)

                visited.add(url)

            except Exception as e:
                print(f"  → Error scraping {url}: {e}")
                visited.add(url)
                continue

        browser.close()

    # handle integrations page specially — click each tab
    all_chunks.extend(scrape_integrations())

    # save to json
    os.makedirs("data", exist_ok=True)
    with open("data/scraped.json", "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\n✅ Done! Total chunks: {len(all_chunks)}")
    print(f"✅ Saved to data/scraped.json")
    return all_chunks

def scrape_integrations():
    """Special handler for the integrations page — clicks each category tab"""
    chunks = []
    tabs = ["Logistics", "CRM", "E-commerce", "Helpdesk", "Marketing", "ERP"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("\nScraping integrations tabs...")

        page.goto("https://debales.ai/integrations", timeout=15000)
        page.wait_for_timeout(2000)

        for tab in tabs:
            try:
                print(f"  → Clicking tab: {tab}")
                page.click(f"text={tab}")
                page.wait_for_timeout(1500)
                text = page.inner_text("body")
                tab_chunks = chunk_text(text, f"https://debales.ai/integrations#{tab.lower()}")
                chunks.extend(tab_chunks)
                print(f"     {len(tab_chunks)} chunks from {tab}")
            except Exception as e:
                print(f"     Error on tab {tab}: {e}")

        browser.close()

    return chunks

if __name__ == "__main__":
    scrape_site()