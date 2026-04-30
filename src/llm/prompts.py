import json
import pandas as pd

SYSTEM_PROMPT = """You are an expert food critic and AI restaurant recommendation engine. 
Your goal is to analyze a list of filtered restaurants and recommend the top 3-5 options based on the user's specific preferences. 
You must explain *why* each restaurant is a great fit, highlighting its cuisines, rating, or cost.
Output your response STRICTLY as a JSON object with a single key "recommendations" that contains an array of objects.
Each object in the array must have the following keys:
- "name": Restaurant Name
- "cuisine": Cuisine Type
- "rating": Average Rating
- "cost": Estimated Cost
- "reasoning": Your expert explanation (1-2 sentences) of why it was chosen.
"""

def build_user_prompt(filtered_df: pd.DataFrame, preferences: dict) -> str:
    """
    Formats the filtered restaurants and user preferences into a string prompt.
    """
    # Keep only relevant columns to save tokens and prevent context overflow
    cols_to_keep = ['name', 'location', 'cuisines', 'rate', 'approx_cost(for_two_people)', 'dish_liked']
    available_cols = [c for c in cols_to_keep if c in filtered_df.columns]
    
    restaurants_data = filtered_df[available_cols].to_dict(orient='records')
    
    prompt = f"User Preferences:\n{json.dumps(preferences, indent=2)}\n\n"
    prompt += f"Filtered Restaurants Available:\n{json.dumps(restaurants_data, indent=2)}\n\n"
    prompt += "Based on the preferences, pick the top 3-5 restaurants and provide your reasoning in the requested JSON format."
    
    return prompt
