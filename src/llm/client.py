import os
import json
from dotenv import load_dotenv
from groq import Groq
from .prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

def get_recommendations(filtered_df, user_preferences):
    """
    Calls the Groq API to get restaurant recommendations based on filtered data.
    Returns a parsed JSON list of recommended restaurants.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in a .env file.")
        
    client = Groq(api_key=api_key)
    
    # Construct the user prompt with the filtered dataframe
    user_prompt = build_user_prompt(filtered_df, user_preferences)
    
    try:
        # We use llama-3.1-8b-instant for fast, efficient JSON generation
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        content = chat_completion.choices[0].message.content
        
        # Parse the JSON response
        try:
            results = json.loads(content)
            if "recommendations" in results:
                return results["recommendations"]
            return results
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON. Raw response:")
            print(content)
            return []
            
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return []
