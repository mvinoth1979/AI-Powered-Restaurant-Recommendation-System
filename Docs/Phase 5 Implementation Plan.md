# Implementation Plan: Phase 5 (Web UI Frontend)

> [!NOTE]
> You mentioned "Implement phase 4", but **Phase 4 (Backend API)** was just completed and tested successfully in the previous step! I assume you meant the next phase: **Phase 5 (Web UI Frontend Development)**.

Here is the plan to build the final interactive Web UI that connects to our backend engine.

## User Review Required

> [!IMPORTANT]
> I will use **Streamlit** to build the Web UI. It is a rapid UI framework for Python that was included in our initial requirements and is perfect for this AI application. Please confirm if Streamlit is acceptable!

## Proposed Changes

### 1. UI Implementation (`src/ui/app.py`)
I will implement a sleek, interactive Streamlit frontend that serves as the primary mode of input:
- **Hero Section:** A visually appealing title and description for the "AI Restaurant Recommendation System".
- **Input Form:** Sidebar or main page inputs for:
  - Location (Text input)
  - Maximum Budget (Slider or number input)
  - Minimum Rating (Slider from 1.0 to 5.0)
  - Cuisines (Multi-select dropdown)
- **API Integration:** The UI will capture the user's inputs and make an HTTP `POST` request to our running Phase 4 FastAPI Backend (`http://127.0.0.1:8000/api/recommend`).
- **Results Display:** A dynamic, styled presentation of the top 5 restaurants returned by the Groq LLM, clearly formatting the AI's reasoning, ratings, and costs.

### 2. Task Tracker Update
- Add and complete the Phase 5 tasks in `task.md`.

## Verification Plan
1. I will start the Streamlit server using `streamlit run src/ui/app.py`.
2. The UI will be fully interactive and ready for you to use directly in your browser.
