import requests
import pandas as pd
from rapidfuzz import fuzz
import tkinter as tk
from tkinter import messagebox, ttk
from dotenv import load_dotenv  # Import the library
import os
# Load environment variables from .env file
load_dotenv()

# Access the variables from the .env file
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

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
    domain_lower = domain.lower()

    # Calculate exact and partial matches
    exact_match = fuzz.ratio(domain_lower, keyword.lower())
    partial_match = fuzz.partial_ratio(domain_lower, keyword.lower())

    # Split domain name into components (e.g., "innovationexpress.org" -> "innovationexpress")
    domain_main = domain_lower.split('.')[0]
    exact_domain_match = fuzz.ratio(domain_main, keyword.lower())

    # Check for word coverage
    word_coverage = sum(1 for word in words if word in domain_main) / len(words)

    # Penalize long domain names
    length_penalty = max(0, (len(domain_main) - 15) * 0.5)

    # Combine scores
    total_score = (
        exact_match * 0.4 +      # Weight for exact match
        partial_match * 0.3 +    # Weight for partial match
        exact_domain_match * 0.3 +  # Weight for base name match
        word_coverage * 20       # Boost for keyword coverage
    ) - length_penalty           # Penalize overly long domains

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
    keyword_lower = keyword.lower()  # Convert keyword to lowercase for comparison

    for item in data.get('items', []):
        domain = item['displayLink'].lower()  # Convert domain to lowercase
        if domain in seen_domains:  # Skip duplicate domains
            continue
        if domain == keyword_lower:  # Skip exact match with the input keyword
            continue
        if any(excluded in domain for excluded in excluded_domains) or \
           'facebook.com' in domain or 'linkedin.com' in domain or 'instagram.com' in domain or 'youtube.com' in domain:
            continue

        seen_domains.add(domain)  # Mark domain as seen
        score = score_similarity(domain, keyword)
        if score >= 1:  # Filter results with a score of 1 or higher
            results.append({'Domain': domain, 'Similarity Score': score})
    
    return results


def search_and_display(keyword, num_pages, tree):
    try:
        num_pages = int(num_pages)
    except ValueError:
        messagebox.showerror("Error", "Number of pages must be an integer.")
        return

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
        # Clear the tree view
        for item in tree.get_children():
            tree.delete(item)

        # Add new results to the tree view
        for _, row in df.iterrows():
            tree.insert("", "end", values=(row['Domain'], row['Similarity Score']))

        # Save to CSV
        df.to_csv("search_results.csv", index=False)
        messagebox.showinfo("Success", "Results saved to 'search_results.csv'.")
    else:
        messagebox.showinfo("No Results", "No relevant results found.")

def create_gui():
    root = tk.Tk()
    root.title("Google Search Similarity Tool")

    # Input fields
    tk.Label(root, text="Enter Keyword:").grid(row=0, column=0, padx=10, pady=5)
    keyword_entry = tk.Entry(root, width=40)
    keyword_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Number of Pages:").grid(row=1, column=0, padx=10, pady=5)
    pages_entry = tk.Entry(root, width=10)
    pages_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Treeview to display results
    columns = ("Domain", "Similarity Score")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("Domain", text="Domain")
    tree.heading("Similarity Score", text="Similarity Score")
    tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Search button
    search_button = tk.Button(
        root,
        text="Search",
        command=lambda: search_and_display(keyword_entry.get(), pages_entry.get(), tree)
    )
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
