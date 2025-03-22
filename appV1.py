import requests
import time
import string
import concurrent.futures
from threading import Lock


BASE_URL = "http://35.200.185.69:8000/v1/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"}  
INITIAL_WAIT = 0.2  # Start with a small delay
MAX_WAIT = 5  # Maximum delay when rate limited
OUTPUT_FILE = "namesV1.txt"


rate_lock = Lock()
rate_limit_wait = INITIAL_WAIT  


# Ignores system proxy settings
session = requests.Session()
session.trust_env = False 


def fetch_names(query):
    """Fetch autocomplete results for a given query with adaptive rate limiting."""
    global rate_limit_wait
    
    while True:  # Retry loop to handle rate limits
        try:
            response = session.get(BASE_URL + query, headers=HEADERS)

            if response.status_code == 429:  # Rate limited
                with rate_lock:
                    rate_limit_wait = min(rate_limit_wait * 1.5, MAX_WAIT)  # Increase wait time

                print(f"Rate limit hit !!")
                time.sleep(rate_limit_wait)
                continue  # Retry after wait

            response.raise_for_status()
            
            with rate_lock:
                rate_limit_wait = max(rate_limit_wait * 0.8, INITIAL_WAIT)  # Gradually decrease wait time

            return response.json().get("results", [])  # Assuming "results" key

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {query}: {e}")
            time.sleep(2)  # Small wait before retrying
            return []


def explore_names():
    """Explore the API by recursively fetching all possible names."""
    found_names = set()
    queue = [a + b for a in string.ascii_lowercase for b in string.ascii_lowercase]  # aa-zz
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
