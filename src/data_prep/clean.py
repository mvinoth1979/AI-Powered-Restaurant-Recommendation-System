import pandas as pd
import numpy as np

def clean_data(df):
    """
    Cleans and preprocesses the Zomato dataset.
    Handles missing values, standardizes column names, and normalizes text.
    """
    print("Starting data cleaning...")
    # Work on a copy
    df = df.copy()
    
    # 1. Standardize column names (lowercase, replace spaces with underscores)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # 2. Handle missing values for text columns
    text_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in text_cols:
        df[col] = df[col].fillna("Unknown").str.strip()
        
    # 3. Handle missing values for numeric columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        # Impute with median to avoid outlier skewness
        median_val = df[col].median()
        if pd.isna(median_val):
            median_val = 0
        df[col] = df[col].fillna(median_val)
        
    # 4. Specific Data Normalization (if applicable)
    # Ensure cost and rating are numeric types if they were loaded as strings
    if 'cost' in df.columns and df['cost'].dtype == 'object':
        df['cost'] = pd.to_numeric(df['cost'].str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        
    if 'rating' in df.columns and df['rating'].dtype == 'object':
        df['rating'] = pd.to_numeric(df['rating'].str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)

    print(f"Data cleaning complete. Output shape: {df.shape}")
    return df
