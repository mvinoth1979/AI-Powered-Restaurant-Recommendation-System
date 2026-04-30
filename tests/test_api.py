import requests
import json
import sys

def run_live_test():
    url = "http://127.0.0.1:8000/api/recommend"
    
    # Test criteria provided by user:
    # Location: Bellandur, Budget: 2000, rating: 4.0
    payload = {
        "location": "Bellandur",
        "budget_max": 2000,
        "min_rating": 4.0,
        "cuisines": [] 
    }
    
    print(f"=== Testing Live Phase 4 API at {url} ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("\nAPI Response Received Successfully!")
            data = response.json()
            recs = data.get("recommendations", [])
            print(f"\nGot {len(recs)} Top Restaurants:\n")
            for i, r in enumerate(recs, 1):
                print(f"{i}. {r.get('name')}")
                print(f"   Cuisine: {r.get('cuisine')}")
                print(f"   Rating: {r.get('rating')}")
                print(f"   Cost: {r.get('cost')}")
                print(f"   Reasoning: {r.get('reasoning')}\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Is the FastAPI server running?")
        sys.exit(1)

if __name__ == "__main__":
    run_live_test()
