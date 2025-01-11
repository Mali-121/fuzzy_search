import requests
import pandas as pd
from rapidfuzz import fuzz

API_KEY = "AIzaSyAY3Fa2B-WVkHQxTwiF6oynpNLwS6t4oY0"
SEARCH_ENGINE_ID = "950bbb4edb1b84bb7"

def google_search(keyword, start=1):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={keyword}&start={start}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return {}

def score_similarity(domain, keyword):
    # Tokenize the keyword
    words = keyword.lower().split()
    domain_lower = domain.lower()

    # Calculate exact and partial matches
    exact_match = fuzz.ratio(domain_lower, keyword.lower())
    partial_match = fuzz.partial_ratio(domain_lower, keyword.lower())

    # Split domain name into components (e.g., "innovationexpress.org" -> "innovationexpress")
    domain_main = domain_lower.split('.')[0]

    # Boost scores for exact matches with the main domain
    exact_domain_match = fuzz.ratio(domain_main, keyword.lower())

    # Assign weight for domain suffix
    domain_suffix = domain.split('.')[-1].lower()
    suffix_weight = 0
    if domain_suffix in ['com', 'org', 'net', '.info', 'ca', 'co', 'uk', '.co.uk', '.biz', '.com.au']:
        suffix_weight = 5
    elif domain_suffix in ['io', 'ai', 'tech']:
        suffix_weight = 3

    # Combine scores
    total_score = (exact_match * 0.4 + partial_match * 0.4 + exact_domain_match * 0.2) + suffix_weight

    # Convert total score into a 1-5 scale
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
    excluded_domains = [
        'reddit.com', 'quora.com', 'pinterest.com', 'youtube.com', 'linkedin.com',
        'github.com', 'tiktok.com', 'wikipedia.com', 'twitter.com', 'x.com',
        'wn.com', 'justdial.com', 'humbleworth.com', 'ebay.com'
    ]
    seen_domains = set()  # Track already processed domains
    results = []

    for item in data.get('items', []):
        domain = item['displayLink']
        if domain in seen_domains:  # Skip duplicate domains
            continue
        if any(excluded in domain for excluded in excluded_domains) or \
           'facebook.com' in domain or 'linkedin.com' in domain or 'instagram.com' in domain or 'youtube.com' in domain:
            continue

        seen_domains.add(domain)  # Mark domain as seen
        score = score_similarity(domain, keyword)
        if score >= 1:  # Filter results with a score of 1 or higher
            results.append({'Domain': domain, 'Similarity Score': score})
    
    return results

def main():
    keyword = input("Enter a keyword to search: ").strip()
    try:
        num_pages = int(input("Enter the number of pages to search: ").strip())
    except ValueError:
        print("Invalid input. Defaulting to 3 pages.")
        num_pages = 3

    all_results = []
    for start in range(1, num_pages * 10, 10):
        data = google_search(keyword, start=start)
        if 'items' in data:
            results = process_results(data, keyword)
            all_results.extend(results)
        else:
            print(f"No results found for start={start}")
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
