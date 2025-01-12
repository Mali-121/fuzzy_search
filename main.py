import requests
import pandas as pd
from rapidfuzz import fuzz
import tkinter as tk
from tkinter import messagebox, ttk
from dotenv import load_dotenv
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
        exact_match * 0.4 +
        partial_match * 0.3 +
        exact_domain_match * 0.3 +
        word_coverage * 20
    ) - length_penalty

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
    seen_domains = set()
    results = []
    keyword_lower = keyword.lower()

    for item in data.get('items', []):
        domain = item['displayLink'].lower()
        if domain in seen_domains:
            continue
        if domain == keyword_lower:
            continue
        if any(excluded in domain for excluded in excluded_domains):
            continue

        seen_domains.add(domain)
        score = score_similarity(domain, keyword)
        if score >= 1:
            results.append({'Domain': domain, 'Similarity Score': score})
    return results


def search_and_display(keyword, num_pages, tree_low, tree_high):
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
        # Clear the tree views
        for item in tree_low.get_children():
            tree_low.delete(item)
        for item in tree_high.get_children():
            tree_high.delete(item)

        # Add results to the respective tree views
        for _, row in df.iterrows():
            if row['Similarity Score'] in [1, 2]:
                tree_low.insert("", "end", values=(row['Domain'], row['Similarity Score']))
            else:
                tree_high.insert("", "end", values=(row['Domain'], row['Similarity Score']))

        # Save to CSV
        df.to_csv("search_results.csv", index=False)
        messagebox.showinfo("Success", "Results saved to 'search_results.csv'.")
    else:
        messagebox.showinfo("No Results", "No relevant results found.")


def create_gui():
    root = tk.Tk()
    root.title("Google Search Similarity Tool")
    root.geometry("900x600")
    root.configure(bg="#f7f7f7")

    # Input fields
    header = tk.Label(root, text="Search Similarity Tool", font=("Arial", 16, "bold"), bg="#f7f7f7", fg="#333")
    header.grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(root, text="Enter Keyword:", bg="#f7f7f7", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    keyword_entry = tk.Entry(root, width=40, font=("Arial", 12))
    keyword_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(root, text="Number of Pages:", bg="#f7f7f7", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    pages_entry = tk.Entry(root, width=10, font=("Arial", 12))
    pages_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    # Treeviews for low and high ratings
    columns = ("Domain", "Similarity Score")

    frame_low = tk.LabelFrame(root, text="Low Ratings (1 & 2)", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#d9534f")
    frame_low.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
    tree_low = ttk.Treeview(frame_low, columns=columns, show="headings", height=10)
    tree_low.heading("Domain", text="Domain")
    tree_low.heading("Similarity Score", text="Similarity Score")
    tree_low.pack(fill="both", expand=True)

    frame_high = tk.LabelFrame(root, text="High Ratings (3 to 5)", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#5cb85c")
    frame_high.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
    tree_high = ttk.Treeview(frame_high, columns=columns, show="headings", height=10)
    tree_high.heading("Domain", text="Domain")
    tree_high.heading("Similarity Score", text="Similarity Score")
    tree_high.pack(fill="both", expand=True)

    # Scrollbars
    scrollbar_low = ttk.Scrollbar(frame_low, orient="vertical", command=tree_low.yview)
    tree_low.configure(yscrollcommand=scrollbar_low.set)
    scrollbar_low.pack(side="right", fill="y")

    scrollbar_high = ttk.Scrollbar(frame_high, orient="vertical", command=tree_high.yview)
    tree_high.configure(yscrollcommand=scrollbar_high.set)
    scrollbar_high.pack(side="right", fill="y")

    # Search button
    search_button = tk.Button(
        root,
        text="Search",
        font=("Arial", 12, "bold"),
        bg="#0275d8",
        fg="white",
        command=lambda: search_and_display(keyword_entry.get(), pages_entry.get(), tree_low, tree_high)
    )
    search_button.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
