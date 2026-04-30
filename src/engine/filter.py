import pandas as pd
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserPreferences:
    location: Optional[str] = None
    budget_max: Optional[float] = None
    cuisines: Optional[List[str]] = None
    min_rating: Optional[float] = None
    
def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences, top_k: int = 15) -> pd.DataFrame:
    """
    Phase 2: Core Search & Filtering Engine
    Filters the cleaned dataset based on user preferences and returns the top_k results.
    """
    filtered = df.copy()
    
    # Filter by Location
    if prefs.location:
        loc = prefs.location.lower().strip()
        filtered = filtered[
            filtered['location'].str.lower().str.contains(loc, na=False) |
            filtered['listed_in(city)'].str.lower().str.contains(loc, na=False)
        ]
        
    # Filter by Cuisines (matches any of the cuisines requested)
    if prefs.cuisines and len(prefs.cuisines) > 0:
        cuisine_mask = pd.Series([False] * len(filtered), index=filtered.index)
        for cuisine in prefs.cuisines:
            c = cuisine.lower().strip()
            cuisine_mask |= filtered['cuisines'].str.lower().str.contains(c, na=False)
        filtered = filtered[cuisine_mask]
        
    # Filter by Budget
    if prefs.budget_max is not None:
        filtered['approx_cost(for_two_people)'] = pd.to_numeric(filtered['approx_cost(for_two_people)'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        filtered = filtered[filtered['approx_cost(for_two_people)'] <= prefs.budget_max]
        
    # Filter by Minimum Rating
    if prefs.min_rating is not None:
        filtered['rate'] = pd.to_numeric(filtered['rate'].astype(str).str.extract(r'(\d+\.\d+|\d+)')[0], errors='coerce')
        filtered = filtered[filtered['rate'] >= prefs.min_rating]
        
    # Top-K Retrieval based on highest rating, with votes as tie-breaker
    if not filtered.empty:
        filtered = filtered.sort_values(by=['rate', 'votes'], ascending=[False, False])
        filtered = filtered.head(top_k)
        
    return filtered
