import requests
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

API_KEY = "AIzaSyAY3Fa2B-WVkHQxTwiF6oynpNLwS6t4oY0"
SEARCH_ENGINE_ID = "950bbb4edb1b84bb7"

def scrape_domains_from_humbleworth():
    url = "https://humbleworth.com/gems"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    domain_data = []

    # Select all cards or relevant containers
    cards = soup.select("div.rounded-lg.relative.shadow-md")  # Card container based on the earlier screenshot
    for card in cards:
        try:
            # Extract domain name from the <h2> tag
            domain_name = card.select_one("h2.text-xl.font-semibold.mb-4.flex.items-center").text.strip()

            # Extract auction value from the <div> tag
            auction_value = card.select_one("div.flex.flex-wrap.items-center.justify-between.gap-3").text.strip()

            domain_data.append({"Domain Name": domain_name, "Auction Value": auction_value})
        except AttributeError as e:
            print(f"Error parsing a card. Skipping... {e}")

    return domain_data

def google_search(keyword, start=1):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={keyword}&start={start}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return {}

def score_similarity(domain, keyword):
    words = keyword.lower().split()
    match_score = sum([fuzz.partial_ratio(word, domain.lower()) for word in words]) / len(words)
    domain_suffix = domain.split('.')[-1].lower()
    suffix_weight = 0

    if domain_suffix in ['com', 'org', 'net']:
        suffix_weight = 5
    elif domain_suffix in ['io', 'ai', 'tech']:
        suffix_weight = 3

    if keyword.lower() in domain.lower():
        match_score += 15  # Higher boost for exact keyword presence

    total_score = match_score + suffix_weight

    if total_score > 90:
        return 5
    elif total_score > 75:
        return 4
    elif total_score > 50:
        return 3
    elif total_score > 30:
        return 2
    else:
        return 1

def process_results(data, keyword):
    excluded_domains = ['reddit.com', 'quora.com', 'pinterest.com', 'youtube.com', 'linkedin.com', 'github.com']
    results = []
    for item in data.get('items', []):
        domain = item['displayLink']
        title = item.get('title', 'No Title Available')
        if any(excluded in domain for excluded in excluded_domains) or \
           'facebook.com' in domain or 'linkedin.com' in domain or 'instagram.com' in domain or 'youtube.com' in domain:
            continue
        score = score_similarity(domain, keyword)
        if score >= 1:  # Filter results with a score of 1 or higher
            results.append({'Domain': domain, 'Page Title': title, 'Similarity Score': score})
    return results

def main():
    print("Scraping domains from Humbleworth...")
    scraped_data = scrape_domains_from_humbleworth()

    if not scraped_data:
        print("No domains found. Exiting.")
        return

    print("Domains scraped successfully. Starting Google search...")

    all_results = []
    for domain_entry in scraped_data:
        domain_name = domain_entry["Domain Name"]
        auction_value = domain_entry["Auction Value"]
        print(f"Searching for: {domain_name}")
        data = google_search(domain_name)
        if 'items' in data:
            results = process_results(data, domain_name)
            for result in results:
                result['Auction Value'] = auction_value
                all_results.append(result)

    df = pd.DataFrame(all_results)
    if not df.empty:
        print(df)
        print(f"\nCount of results with score 1 or higher: {len(df)}")
        df.to_csv("search_results.csv", index=False)
        print("Results saved to 'search_results.csv'.")
    else:
        print("No relevant results found.")

if __name__ == "__main__":
    main()
