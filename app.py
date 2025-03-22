 # install dependencies
import requests
import time
import string


BASE_URL = "http://35.200.185.69:8000/v1/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"} 
RATE_LIMIT_WAIT = 1  


# Ignores system proxy settings
session = requests.Session()
session.trust_env = False 


def fetch_names(query):
    """Fetch autocomplete results for a given query."""
    try:
        response = session.get(BASE_URL + query, headers=HEADERS)
        
        if response.status_code == 429:  # Rate limited
            print("Rate limit hit! Waiting...")
            time.sleep(RATE_LIMIT_WAIT * 2)  # Wait longer
            return fetch_names(query)  # Retry
        
        response.raise_for_status()
        return response.json().get("results", [])  # Assuming response has a "results" key

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {query}: {e}")
        return []


def explore_names():
    """Explore the API by recursively fetching all possible names."""
    found_names = set()
    queue = list(string.ascii_lowercase)  # Start with a-z
    request_count = 0  # Track API calls

    while queue:
        query = queue.pop(0)
        print(f"Fetching: {query}")

        names = fetch_names(query)
        request_count += 1  # Increment request count
        new_names = set(names) - found_names
        found_names.update(new_names)

        # Expand search with discovered prefixes
        if new_names:
            queue.extend(name for name in new_names if len(name) > len(query))

        time.sleep(RATE_LIMIT_WAIT)  # Avoid hitting rate limits

    return found_names, request_count


if __name__ == "__main__":
    names, total_requests = explore_names()
    
    # Save results
    with open("namesV1.txt", "w") as f:
        for name in sorted(names):
            f.write(name + "\n")

    print(f"Total names collected: {len(names)}")
    print(f"Total API requests made: {total_requests}")