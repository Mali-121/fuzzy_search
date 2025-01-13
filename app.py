from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
from rapidfuzz import fuzz
import aiohttp
import asyncio
from dotenv import load_dotenv
import requests_cache

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Enable caching for 1 hour
requests_cache.install_cache("google_search_cache", expire_after=3600)

app = Flask(__name__)

# Function to perform async Google search
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def google_search_async(keyword, pages):
    urls = [
        f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={keyword}&start={start}"
        for start in range(1, pages * 10, 10)
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

def score_similarity(domain, keyword):
    words = keyword.lower().split()
    domain_lower = domain.lower()
    exact_match = fuzz.ratio(domain_lower, keyword.lower())
    partial_match = fuzz.partial_ratio(domain_lower, keyword.lower())
    domain_main = domain_lower.split('.')[0]
    exact_domain_match = fuzz.ratio(domain_main, keyword.lower())
    word_coverage = sum(1 for word in words if word in domain_main) / len(words)
    length_penalty = max(0, (len(domain_main) - 15) * 0.5)

    total_score = (
        exact_match * 0.4 +
        partial_match * 0.3 +
        exact_domain_match * 0.3 +
        word_coverage * 20
    ) - length_penalty

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
    seen_domains = set()
    results = []
    keyword_lower = keyword.lower()

    for response in data:
        for item in response.get('items', []):
            domain = item['displayLink'].lower()
            if domain in seen_domains or domain == keyword_lower:
                continue
            if any(excluded in domain for excluded in excluded_domains):
                continue
            seen_domains.add(domain)
            score = score_similarity(domain, keyword)
            results.append({'Domain': domain, 'Similarity Score': score})
    return results

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')  # Ensure your HTML file is saved in a folder named "templates"

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    keyword = data.get('keyword', '')
    pages = data.get('pages', 1)

    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400

    try:
        pages = int(pages)  # Convert pages to an integer
    except ValueError:
        return jsonify({'error': 'Number of pages must be an integer'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    raw_results = loop.run_until_complete(google_search_async(keyword, pages))
    processed_results = process_results(raw_results, keyword)

    df = pd.DataFrame(processed_results)
    if not df.empty:
        df.to_csv('search_results.csv', index=False)
        return jsonify({'results': processed_results})
    else:
        return jsonify({'message': 'No relevant results found.'})


if __name__ == '__main__':
    app.run(debug=True)
