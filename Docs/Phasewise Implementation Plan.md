# Phase-Wise Implementation Plan

This document outlines the detailed technical implementation strategy for the AI-Powered Restaurant Recommendation System, broken down by phases.

---

## Phase 1: Data Preparation (`src/data_prep/`)
**Objective:** Ingest the raw Zomato dataset, clean it, and save it for rapid querying.

- **`ingest.py`**: Connects to the Hugging Face `datasets` library to pull `ManikaSaini/zomato-restaurant-recommendation` and converts the train split into a Pandas DataFrame.
- **`clean.py`**: 
  - Standardizes column names (lowercase, underscores).
  - Handles missing values (imputes median for numerics like cost and rating, fills missing text with "Unknown").
  - Dynamically cleans formatting (e.g., converts string ratings like `"4.1/5"` to numeric floats).
- **`run.py`**: Pipeline orchestration script. Executes ingestion, runs cleaning, and outputs the final result to `data/processed/processed_zomato.csv`.

---

## Phase 2: Core Search Engine (`src/engine/`)
**Objective:** Filter the cleaned dataset efficiently to retrieve a targeted subset before engaging the LLM.

- **`filter.py`**:
  - Implements a `UserPreferences` Pydantic/dataclass schema capturing `location`, `budget_max`, `cuisines`, and `min_rating`.
  - Applies dynamic pandas masking to filter the DataFrame.
  - Truncates the results to a "Top K" limit (default: 15) by sorting by `rate` and `votes` to prevent LLM context window overflow.
- **`tests/test_engine.py`**: Pytest/Unittest suite to verify correct logical filtering by location and rating constraints.

---

## Phase 3: LLM Integration (`src/llm/`)
**Objective:** Inject the filtered restaurants into a prompt and use a Large Language Model to reason and select the absolute best choices.

- **`prompts.py`**: Defines the `SYSTEM_PROMPT` (establishing the "Expert Food Critic" persona) and formats the `UserPreferences` and filtered DataFrame into a structured prompt.
- **`client.py`**: 
  - Connects to the **Groq API** (`llama-3.1-8b-instant`) for blazing-fast inference.
  - Enforces structured JSON output (`response_format={"type": "json_object"}`).
  - Parses the raw LLM string into a Python list of dictionaries containing `name`, `cuisine`, `rating`, `cost`, and `reasoning`.

---

## Phase 4: Backend API (`src/api/`)
**Objective:** Expose the Core Engine (Phase 2) and LLM logic (Phase 3) as a robust RESTful API.

- **`main.py`**: 
  - Utilizes **FastAPI** to serve the application.
  - Loads the `processed_zomato.csv` into memory on startup.
  - Exposes `POST /api/recommend` which accepts a JSON payload mapping to `RecommendationRequest`.
  - Seamlessly orchestrates the flow from request -> Engine filter -> Groq LLM -> Response.
- **`tests/test_api.py`**: End-to-End test script executing HTTP requests against `http://127.0.0.1:8000/api/recommend`.

---

## Phase 5: Web UI Frontend (`src/ui/`) *(Pending)*
**Objective:** Build an interactive frontend interface for users to select preferences and view AI recommendations.

- **`app.py`**: 
  - Built with **Streamlit** for rapid UI development.
  - Features dynamic input sliders for budget and rating, dropdowns for cuisine selection, and text input for location.
  - Consumes the Phase 4 Backend API (`POST /api/recommend`).
  - Renders the final Top 5 recommendations in aesthetically pleasing cards, highlighting the AI reasoning.
