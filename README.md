fuzzy_search is a Python-based tool for performing domain search and similarity scoring using Google's Custom Search API. The program leverages fuzzy matching algorithms to rank and score search results based on their similarity to a given keyword.

Features
Asynchronous Search: Utilizes aiohttp for faster and efficient parallel search requests.
Similarity Scoring: Ranks domains based on fuzzy matching, exact matches, and keyword coverage.
GUI Interface: Interactive interface built with Tkinter for entering search queries and viewing results.
Caching: Implements requests_cache to store API responses for faster subsequent searches.
CSV Export: Save search results to a CSV file for future reference.
Requirements
To run this project, ensure you have the following:

Python 3.7 or higher
Installed dependencies (listed below)
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/fuzzy_search.git
cd fuzzy_search
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up a .env file:

Create a .env file in the root directory with the following contents:
env
Copy code
API_KEY=your_google_api_key
SEARCH_ENGINE_ID=your_search_engine_id
Usage
Run the program:

bash
Copy code
python main.py
Enter your search keyword and the number of pages to search.

View the results in the GUI and save them as a CSV file.

How It Works
Search: Fetches search results using Google Custom Search API.
Fuzzy Matching: Scores results using rapidfuzz to determine similarity.
Filtering: Excludes unwanted domains and duplicates.
Display: Results are displayed in a table, separated into two categories:
Ratings 1–2
Ratings 3–5
Dependencies
requests
aiohttp
pandas
rapidfuzz
tkinter
requests-cache
python-dotenv
Install them using:

bash
Copy code
pip install -r requirements.txt
