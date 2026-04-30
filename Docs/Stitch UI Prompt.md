# Prompt for Google Stitch (Next.js UI Generation)

**Context:**
We are building an AI-Powered Restaurant Recommendation System inspired by Zomato. The backend is a FastAPI service that processes a real-world restaurant dataset, filters based on user inputs, and uses an LLM (Groq) to rank and reason about the top restaurant choices.

We need a modern, premium, and highly interactive front-end web application built using **Next.js** and **Tailwind CSS**.

**Task for Google Stitch:**
Please generate the complete front-end code for the "AI Restaurant Recommender" using Next.js, React, and Tailwind CSS. The UI should have a vibrant, dynamic design with glassmorphism effects, smooth micro-animations, and a highly responsive layout.

**Core Pages/Components Required:**

1.  **Landing Page / Hero Section:**
    *   A visually stunning hero section with a catchy headline (e.g., "Discover Your Next Great Meal with AI").
    *   A dynamic search/filter bar to collect user preferences:
        *   **Location:** Dropdown or text input (e.g., Delhi, Bangalore).
        *   **Budget:** Radio buttons or slider (Low, Medium, High).
        *   **Cuisine:** Multi-select dropdown or chips (e.g., Italian, Chinese, North Indian).
        *   **Minimum Rating:** Star rating selector or slider.
        *   **Custom Preferences:** A text area for additional requests (e.g., "rooftop seating", "family-friendly").
    *   A prominent, animated "Find Restaurants" call-to-action button.

2.  **Loading State:**
    *   A beautiful skeleton loader or a bespoke loading animation with playful, food-related text (e.g., "Consulting the AI Chef...") while the backend fetches recommendations.

3.  **Results Dashboard:**
    *   A clear, accessible grid or list layout presenting the AI's recommendations.
    *   Each restaurant card should display:
        *   Restaurant Name (Prominent heading).
        *   Cuisine Tags.
        *   Average Rating (Visual star representation).
        *   Estimated Cost (e.g., "$$" or exact text).
        *   **AI's Reasoning:** A highlighted section or accordion showing the natural-language explanation of why this restaurant was recommended.

4.  **Design System & Aesthetics:**
    *   Use a curated, harmonious color palette (e.g., sleek dark mode or vibrant, appetizing colors).
    *   Implement modern typography (e.g., Inter, Outfit) instead of browser defaults.
    *   Add hover effects on cards and buttons.
    *   Ensure proper accessibility and responsive design for mobile, tablet, and desktop.

**Technical Constraints:**
*   Use Next.js App Router.
*   Use Tailwind CSS for styling.
*   The components should be ready to integrate with a RESTful API (FastAPI backend) via standard `fetch` calls. For now, use mock data that represents the expected backend output structure (Name, Cuisine, Rating, Cost, AI Reasoning).
