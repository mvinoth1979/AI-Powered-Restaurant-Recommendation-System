import pandas as pd
from datasets import load_dataset

def load_zomato_dataset(repo_id="ManikaSaini/zomato-restaurant-recommendation"):
    """
    Downloads the Zomato dataset from Hugging Face and returns it as a Pandas DataFrame.
    """
    print(f"Loading dataset from Hugging Face: {repo_id}...")
    try:
        # Load the dataset
        dataset = load_dataset(repo_id)
        
        # Most HF datasets use the 'train' split by default
        if 'train' in dataset:
            df = pd.DataFrame(dataset['train'])
        else:
            # Fallback if there's only one split or different naming
            split_name = list(dataset.keys())[0]
            df = pd.DataFrame(dataset[split_name])
            
        print(f"Successfully loaded {len(df)} records.")
        return df
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return None
