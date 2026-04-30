import os
import sys
import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to sys.path to resolve imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from engine.filter import filter_restaurants, UserPreferences
from llm.client import get_recommendations

app = FastAPI(title="AI Restaurant Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset once when app starts
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", "processed_zomato.csv")
try:
    df = pd.read_csv(data_path, low_memory=False)
    print(f"Successfully loaded {len(df)} records into the API.")
except Exception as e:
    df = None
    print(f"Warning: Could not load dataset at startup: {e}")

class RecommendationRequest(BaseModel):
    location: Optional[str] = None
    budget_max: Optional[float] = None
    cuisines: Optional[List[str]] = None
    min_rating: Optional[float] = None

@app.get("/api/locations")
def get_locations():
    if df is None or df.empty:
        return {"locations": []}
    # Get unique valid locations
    locations = sorted([str(loc) for loc in df['location'].dropna().unique() if str(loc).strip() and str(loc) != 'Unknown'])
    return {"locations": locations}

@app.post("/api/recommend")
def recommend_restaurants(req: RecommendationRequest):
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded.")
        
    prefs = UserPreferences(
        location=req.location,
        budget_max=req.budget_max,
        cuisines=req.cuisines,
        min_rating=req.min_rating
    )
    
    prefs_dict = {
        "Location": req.location,
        "Budget (Max)": req.budget_max,
        "Cuisines Preferred": req.cuisines,
        "Minimum Rating": req.min_rating
    }
    
    # Filter using our engine
    filtered_df = filter_restaurants(df, prefs, top_k=15)
    
    if filtered_df.empty:
        return {"recommendations": [], "message": "No restaurants matched your exact criteria."}
        
    # Get recommendations from Groq
    try:
        recommendations = get_recommendations(filtered_df, prefs_dict)
        # Ensure we return at most 5 as requested by the user prompt
        if isinstance(recommendations, list) and len(recommendations) > 5:
            recommendations = recommendations[:5]
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
