import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/recommend"

st.set_page_config(page_title="AI Restaurant Finder", page_icon="🍽️", layout="wide")

st.title("🍽️ AI-Powered Restaurant Recommendation System")
st.markdown("Find the perfect dining spot curated by an expert AI food critic based on your exact preferences.")

# Sidebar for inputs
st.sidebar.header("Your Preferences")

def fetch_locations():
    try:
        res = requests.get(API_URL.replace("/recommend", "/locations"), timeout=5)
        if res.status_code == 200:
            locs = res.json().get("locations", [])
            if locs:
                return locs
    except Exception as e:
        st.sidebar.error(f"Backend API not ready: {e}")
    return []

locations_list = fetch_locations()
location_options = [""] + locations_list

location = st.sidebar.selectbox("Location (Type to search)", options=location_options, index=0)
budget_max = st.sidebar.slider("Maximum Budget (for two)", min_value=100, max_value=5000, value=1500, step=100)
min_rating = st.sidebar.slider("Minimum Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)

cuisines_input = st.sidebar.text_input("Cuisines (comma separated)", placeholder="e.g. Cafe, Italian, North Indian")

if st.sidebar.button("Find Restaurants", type="primary"):
    with st.spinner("Our AI Food Critic is reviewing menus..."):
        cuisines_list = [c.strip() for c in cuisines_input.split(',')] if cuisines_input else []
        
        payload = {
            "location": location if location else None,
            "budget_max": budget_max,
            "min_rating": min_rating,
            "cuisines": cuisines_list
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                recs = data.get("recommendations", [])
                
                if not recs:
                    st.warning("No restaurants matched your criteria. Try loosening your filters.")
                else:
                    st.success(f"Found {len(recs)} Top Recommendations!")
                    for idx, r in enumerate(recs, 1):
                        with st.container():
                            st.subheader(f"{idx}. {r.get('name')}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Rating", f"{r.get('rating')} ⭐")
                            col2.metric("Cost for Two", f"₹{r.get('cost')}")
                            col3.write(f"**Cuisine:** {r.get('cuisine')}")
                            
                            st.info(f"**AI Critic's Reasoning:** {r.get('reasoning')}")
                            st.divider()
            else:
                st.error(f"Backend API Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the backend API. Please ensure the FastAPI server is running on http://127.0.0.1:8000")
