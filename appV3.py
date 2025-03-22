 # install dependencies
import requests
import time
import string
import itertools
import concurrent.futures
from threading import Lock


BASE_URL = "http://35.200.185.69:8000/v3/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"}  
OUTPUT_FILE = "namesV3.txt" 

# Initial rate limit settings (will be adjusted dynamically)
MIN_RATE_LIMIT = 0.2  # Start fast
MAX_RATE_LIMIT = 5.0  # Slow down if needed
current_rate_limit = MIN_RATE_LIMIT


# Ignores system proxy settings
session = requests.Session()
session.trust_env = False 


def fetch_names(query):
    """Fetch autocomplete results for a given query and handle rate limits."""
    global current_rate_limit

    try:
        response = session.get(BASE_URL + query, headers=HEADERS)

        if response.status_code == 429:  # Rate limited
            print(f"Rate limit hit!!")

            current_rate_limit = min(current_rate_limit * 1.5, MAX_RATE_LIMIT)  # Increase wait time
            time.sleep(current_rate_limit)
            return fetch_names(query)  # Retry
        
        response.raise_for_status()
        current_rate_limit = max(current_rate_limit / 1.2, MIN_RATE_LIMIT)  # Speed up if no limit hit
        return response.json().get("results", [])  # Assuming response has "results" key

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {query}: {e}")
        return []


def explore_names():
    """Explore the API efficiently using two-character prefixes (letters + numbers+special characters)."""
    found_names = set()
    total_requests = 0

    # Expand search prefixes (letters, numbers, special characters)
    characters = string.ascii_lowercase + string.digits + "+-. "  # a-z, 0-9, and special characters
    queue = [''.join(p) for p in itertools.product(characters, repeat=2)]  # aa-zz, 00-99, etc.

    with open(OUTPUT_FILE, "w") as f, concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_query = {executor.submit(fetch_names, query): query for query in queue}

        for future in concurrent.futures.as_completed(future_to_query):
            query = future_to_query[future]
            try:
                names = future.result()
                total_requests += 1
                new_names = set(names) - found_names
                found_names.update(new_names)

                # Print and save names as they are found
                for name in sorted(new_names):
                    print(name)
                    f.write(name + "\n")
                    f.flush()

            except Exception as e:
                print(f"Error processing {query}: {e}")

    print(f"Total names collected: {len(found_names)}")
    print(f"Total API requests made: {total_requests}")


if __name__ == "__main__":
    explore_names()

