import os
from ingest import load_zomato_dataset
from clean import clean_data

def run_phase_1():
    # 1. Ingest Data
    raw_df = load_zomato_dataset()
    if raw_df is None:
        print("Data ingestion failed. Exiting pipeline.")
        return

    # 2. Clean Data
    cleaned_df = clean_data(raw_df)

    # 3. Save Processed Data
    # Path is relative to the project root assuming the script runs from src/data_prep or root
    # Let's ensure the path exists
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "processed_zomato.csv")
    cleaned_df.to_csv(output_path, index=False)
    
    print(f"Phase 1 complete! Cleaned dataset saved to {output_path}")

if __name__ == "__main__":
    run_phase_1()
