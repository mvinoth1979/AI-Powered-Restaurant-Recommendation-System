import sys
import os
import pandas as pd
import json
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from engine.filter import filter_restaurants, UserPreferences
from llm.client import get_recommendations

def run_e2e_test():
    print("=== Starting End-to-End Test (Filtering Engine + Groq LLM) ===")
    
    # 1. Load Data
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "processed_zomato.csv")
    if not os.path.exists(data_path):
        print(f"Error: Processed data not found at {data_path}. Please run Phase 1 first.")
        return
        
    print("\nLoading dataset...")
    df = pd.read_csv(data_path, low_memory=False)
    print(f"Dataset loaded. Total records: {len(df)}")
    
    # 2. Set Mock User Preferences
    prefs = UserPreferences(
        location="Indiranagar",
        budget_max=1500,
        cuisines=["Cafe", "Italian"],
        min_rating=4.2
    )
    prefs_dict = {
        "Location": prefs.location,
        "Budget (Max)": f"Rs. {prefs.budget_max}",
        "Cuisines Preferred": prefs.cuisines,
        "Minimum Rating": prefs.min_rating
    }
    print(f"\nUser Preferences:\n{json.dumps(prefs_dict, indent=2)}")
    
    # 3. Run Filtering Engine
    print("\nFiltering restaurants...")
    filtered_df = filter_restaurants(df, prefs, top_k=10)
    print(f"Filtered down to {len(filtered_df)} top restaurants.")
    if filtered_df.empty:
        print("No restaurants match the criteria. Aborting LLM step.")
        return
        
    # 4. Call Groq LLM
    print("\nSending filtered data to Groq LLM for reasoning and ranking...")
    try:
        recommendations = get_recommendations(filtered_df, prefs_dict)
        print("\n=== AI Recommendations ===")
        if not recommendations:
            print("No recommendations returned or failed to parse.")
            return
            
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.get('name', 'Unknown')}")
            print(f"   Cuisine: {rec.get('cuisine', 'N/A')}")
            print(f"   Rating: {rec.get('rating', 'N/A')}")
            print(f"   Cost: {rec.get('cost', 'N/A')}")
            print(f"   Reasoning: {rec.get('reasoning', 'No reasoning provided.')}")
            
    except Exception as e:
        print(f"\nError during LLM call: {e}")

if __name__ == "__main__":
    run_e2e_test()
