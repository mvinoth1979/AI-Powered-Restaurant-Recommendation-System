# Phase-Wise Architecture: AI-Powered Restaurant Recommendation System

This document outlines the phased development approach for building the AI-powered restaurant recommendation service. 

## Phase 1: Data Preparation & Foundation
**Goal:** Establish a robust and clean data layer.
- **Dataset Retrieval:** Fetch the Zomato restaurant dataset from Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`).
- **Exploratory Data Analysis (EDA):** Understand the dataset schema, data types, missing values, and data distribution.
- **Data Cleaning & Transformation:**
  - Handle missing or null values.
  - Normalize text (e.g., lowercase cuisines, strip whitespace).
  - Convert cost and rating columns into numerical types for easy filtering.
- **Storage:** Save the cleaned dataset locally or load it into an in-memory database (like Pandas DataFrame or SQLite) for quick querying.

## Phase 2: Core Search & Filtering Engine
**Goal:** Build the logic to retrieve relevant restaurants before sending them to the LLM.
- **Input Handling:** Define the schema for user inputs (Location, Budget Range, Cuisines, Minimum Rating).
- **Filtering Logic:** Create a robust filtering function that takes the user inputs and queries the cleaned dataset.
- **Top-K Retrieval:** Implement logic to limit the filtered results (e.g., top 10-20 restaurants) to avoid overwhelming the LLM context window.

## Phase 3: LLM Integration & Prompt Engineering
**Goal:** Leverage an LLM to rank and explain the filtered results.
- **API Setup:** Initialize connection to the chosen LLM (e.g., OpenAI, Gemini, Claude) via API keys.
- **Prompt Design:** 
  - Craft a system prompt giving the LLM the persona of an expert food critic.
  - Format the filtered restaurant data into a structured format (JSON or Markdown) within the prompt.
  - Include user preferences and explicitly instruct the LLM to pick the top 3-5 restaurants and explain *why* they fit the criteria.
- **Response Parsing:** Ensure the LLM outputs a structured response that can be easily displayed (e.g., enforcing a JSON output structure).

## Phase 4: Backend API Development
**Goal:** Expose the core engine and LLM integration via a robust backend API.
- **Framework Selection:** Use a modern Python web framework (e.g., FastAPI or Flask) to create RESTful API endpoints.
- **Endpoint Design:** Create endpoints for receiving user preferences (e.g., `POST /recommendations`) and returning the structured AI recommendations.
- **Integration:** Connect the API routes to the core filtering engine (Phase 2) and LLM client (Phase 3).

## Phase 5: Web UI Frontend Development
**Goal:** Build a modern, decoupled interactive Web UI frontend for the end-user.
- **Framework Selection:** Choose a modern UI framework (e.g., React, Next.js, or Vue.js) to serve as the primary mode of input.
- **Form Creation:** Build intuitive input fields for Location, Budget, Cuisine, Minimum Rating, and extra preferences.
- **API Consumption:** Connect the frontend to the Phase 4 backend API to fetch and display the recommended restaurants, their details, and the AI-generated reasoning in a visually stunning format.

## Phase 6: Testing, Deployment & Refinement
**Goal:** Polish the system and ensure production readiness for both client and server.
- **Edge Case Testing:** Test the system with highly restrictive constraints (e.g., zero matches) and ensure it handles failure gracefully.
- **Latency Optimization:** Optimize data retrieval and API response times (e.g., implementing streaming LLM responses to the frontend).
- **Deployment:** Containerize the backend and frontend (e.g., using Docker) and deploy them to cloud hosting platforms.

## Phase 7: Streamlit Deployment (Free-Tier Alternative)
**Goal:** Provide a lightweight, zero-infrastructure deployment path using Streamlit Community Cloud as a free alternative to the full Next.js + FastAPI stack.

### Why Streamlit?
Streamlit collapses the frontend and backend into a single Python application, eliminating the need for separate API hosting. It deploys for free directly from a GitHub repository with no Docker or server configuration required.

### Architecture Shift
| Component | Phase 5–6 Stack | Phase 7 Streamlit Stack |
|---|---|---|
| **Frontend** | Next.js (Vercel) | Streamlit (Community Cloud) |
| **Backend** | FastAPI (Render) | Streamlit Python runtime (built-in) |
| **Data** | CSV loaded into Pandas | CSV loaded into Pandas (cached) |
| **LLM** | Groq via API | Groq via API (same) |
| **Infra cost** | $0 (free tiers) | $0 (fully free) |

### Implementation Steps
- **App File (`src/ui/streamlit_app.py`):** Build a single-file Streamlit app that:
  - Loads and caches the cleaned dataset with `@st.cache_data`.
  - Renders a sidebar with filter widgets: `st.selectbox` (Location), `st.slider` (Budget, Rating), and `st.multiselect` (Cuisines).
  - On form submission, calls the Phase 2 filtering engine (`filter_restaurants`) directly — no HTTP round-trip needed.
  - Passes the filtered results to the Phase 3 Groq LLM client (`get_recommendations`).
  - Displays each AI recommendation in an `st.card` / `st.expander` with name, cuisine, rating, cost, and reasoning.
- **Secrets Management:** Store `GROQ_API_KEY` in Streamlit Community Cloud's **Secrets** panel (`.streamlit/secrets.toml` locally).
- **Dependencies (`requirements.txt`):** Ensure `streamlit`, `groq`, `pandas`, and `python-dotenv` are listed.

### Deployment to Streamlit Community Cloud
1. Push the repository to GitHub.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
3. Click **New app** → select the repo → set **Main file path** to `src/ui/streamlit_app.py`.
4. Add `GROQ_API_KEY` under **Advanced settings → Secrets**.
5. Click **Deploy** — the app is live at `https://<your-app>.streamlit.app` within minutes.

### Trade-offs vs Full Stack
| Concern | Streamlit | Next.js + FastAPI |
|---|---|---|
| **Setup time** | Minutes | Hours |
| **UI customisation** | Limited (Python widgets) | Full (Tailwind, animations) |
| **Scalability** | Single-threaded per session | Horizontally scalable |
| **Cold-start** | None (always-on free tier) | ~30 s on Render free tier |
| **Best for** | Demos, prototypes, internal tools | Production user-facing apps |
