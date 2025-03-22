 # install dependencies
import requests
import time
import string
import concurrent.futures
from threading import Lock


BASE_URL = "http://35.200.185.69:8000/v2/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"}  
RATE_LIMIT_WAIT = 0.2  # Adjust this dynamically
MAX_RETRIES = 3
OUTPUT_FILE = "namesV2.txt" 


# Ignores system proxy settings
session = requests.Session()
session.trust_env = False 


def fetch_names(query):
    """Fetch autocomplete results for a given query, handling rate limits."""
    global RATE_LIMIT_WAIT
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            response = session.get(BASE_URL + query, headers=HEADERS)
            
            if response.status_code == 429:  # Rate limited
                print(f"Rate limit hit !!")
                time.sleep(RATE_LIMIT_WAIT)

                RATE_LIMIT_WAIT *= 1.5  # Increase wait time gradually
                retries += 1
                continue  # Retry request
            
            response.raise_for_status()
            RATE_LIMIT_WAIT = max(0.2, RATE_LIMIT_WAIT / 1.5)  # Gradually decrease wait time
            return response.json().get("results", [])  # Assuming API returns "results"

        except requests.exceptions.RequestException as e:
            print(f"Error fetching '{query}': {e}")
            return []

    return []



def explore_names():
    """Explore the API efficiently using two-character prefixes (letters + numbers)."""
    found_names = set()
    queue = [a + b for a in string.ascii_lowercase + string.digits for b in string.ascii_lowercase + string.digits]  # a0-z9
    total_requests = 0

    with open(OUTPUT_FILE, "w") as f, concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
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
