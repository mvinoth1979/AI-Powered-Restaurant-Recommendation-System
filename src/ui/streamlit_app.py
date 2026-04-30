"""
Phase 7: Streamlit Community Cloud Deployment
─────────────────────────────────────────────
Self-contained Streamlit app — calls the filter engine and Groq LLM directly,
with no dependency on the FastAPI backend server.

Run locally:
    streamlit run src/ui/streamlit_app.py

Deploy:
    Push to GitHub → share.streamlit.io → set GROQ_API_KEY in Secrets.
"""

import os
import sys
import json
import time
import pandas as pd
import streamlit as st

# ── Path setup (works both locally and on Streamlit Cloud) ────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from engine.filter import filter_restaurants, UserPreferences
from llm.client import get_recommendations

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zomato AI · Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Be+Vietnam+Pro:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif; }
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* Brand header */
.brand { font-size: 2rem; font-weight: 900; font-style: italic;
         background: linear-gradient(135deg, #b7122a, #db313f);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         font-family: 'Plus Jakarta Sans', sans-serif; }
.brand-badge { background: #f0eded; color: #5b403f; padding: 2px 8px;
               border-radius: 4px; font-size: 0.7rem; font-weight: 700;
               letter-spacing: 0.1em; text-transform: uppercase;
               vertical-align: middle; margin-left: 8px; }

/* Card */
.rest-card { background: #ffffff; border: 1px solid #e4bebc; border-radius: 16px;
             padding: 24px; margin-bottom: 20px;
             box-shadow: 0 2px 8px rgba(0,0,0,0.04);
             transition: box-shadow 0.2s; }
.rest-card:hover { box-shadow: 0 6px 20px rgba(183,18,42,0.1); }

/* Rank badge */
.rank { display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; background: #b7122a; color: white;
        border-radius: 50%; font-weight: 700; font-size: 0.85rem;
        margin-right: 10px; flex-shrink: 0; }

/* AI chip */
.ai-chip { display: inline-flex; align-items: center; gap: 4px;
           background: #b7122a; color: #fff; padding: 2px 8px;
           border-radius: 4px; font-size: 0.65rem; font-weight: 700;
           letter-spacing: 0.1em; text-transform: uppercase; }

/* Reasoning box */
.reasoning { background: #ffdad8; border: 1px solid #e4bebc; border-radius: 12px;
             padding: 14px 18px; margin-top: 14px; font-size: 0.9rem;
             color: #410007; line-height: 1.6; }

/* Stat pill */
.pill { display: inline-block; background: #f0eded; border: 1px solid #e4bebc;
        border-radius: 999px; padding: 4px 12px; font-size: 0.82rem;
        font-weight: 600; color: #5b403f; margin-right: 6px; margin-top: 6px; }
.pill-primary { background: #b7122a; color: #fff; border-color: #b7122a; }

/* Sidebar */
[data-testid="stSidebar"] { background: #fcf9f8 !important;
                             border-right: 1px solid #e4bebc !important; }
[data-testid="stSidebar"] h2 { color: #b7122a; font-size: 1rem;
                                font-family: 'Plus Jakarta Sans', sans-serif; }

/* Find button */
.stButton > button { background: linear-gradient(135deg, #b7122a, #db313f) !important;
                     color: white !important; border: none !important;
                     border-radius: 10px !important; font-weight: 700 !important;
                     font-size: 1rem !important; padding: 0.65rem 2rem !important;
                     width: 100% !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.9 !important; }

/* Empty state */
.empty { text-align: center; padding: 60px 20px; color: #8f6f6e; }
.empty h3 { font-size: 1.4rem; font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Data Loading (cached — runs once per session, survives reruns)
# Auto-downloads from Hugging Face if CSV is absent (Streamlit Cloud case)
# ═══════════════════════════════════════════════════════════════════════════════
DATA_PATH = os.path.join(ROOT, "data", "processed", "processed_zomato.csv")

HF_CSV_URL = (
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/main/data/train-00000-of-00001.parquet"
)

def _ensure_dataset_exists():
    """
    Download the processed Zomato CSV from Hugging Face if it isn't on disk.
    Called OUTSIDE @st.cache_data so that st.spinner / st.error work correctly.
    Returns True on success, False on failure.
    """
    if os.path.exists(DATA_PATH):
        return True  # already present

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # ── Try the Hugging Face `datasets` library first ─────────────────────────
    with st.spinner(
        "📥 First run — downloading dataset from Hugging Face. "
        "This takes 1–3 minutes and won't repeat…"
    ):
        try:
            try:
                from datasets import load_dataset
            except ImportError:
                import subprocess
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "datasets"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                from datasets import load_dataset

            dataset = load_dataset(
                "ManikaSaini/zomato-restaurant-recommendation",
                trust_remote_code=True,
            )
            df = dataset["train"].to_pandas()
            df.columns = [c.strip() for c in df.columns]
            df.to_csv(DATA_PATH, index=False)
            return True

        except Exception as primary_err:
            # ── Fallback: direct HTTP download of the parquet ──────────────
            try:
                import urllib.request
                import io

                st.info("Primary download path failed — trying direct download…")
                tmp_parquet = DATA_PATH.replace(".csv", "_tmp.parquet")
                urllib.request.urlretrieve(HF_CSV_URL, tmp_parquet)

                df = pd.read_parquet(tmp_parquet)
                df.columns = [c.strip() for c in df.columns]
                df.to_csv(DATA_PATH, index=False)

                try:
                    os.remove(tmp_parquet)
                except OSError:
                    pass

                return True

            except Exception as fallback_err:
                st.error(
                    f"❌ Could not download the dataset.\n\n"
                    f"Primary error: `{primary_err}`\n\n"
                    f"Fallback error: `{fallback_err}`\n\n"
                    "Please check your internet connection or re-deploy after running "
                    "`python scripts/download_data.py` locally and committing the CSV "
                    "via Git LFS."
                )
                return False

@st.cache_data(show_spinner="Loading restaurant database…")
def load_data() -> pd.DataFrame:
    """Read the CSV from disk and pre-clean numeric columns."""
    if not os.path.exists(DATA_PATH):
        # Should never reach here — _ensure_dataset_exists() is called first
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Pre-clean numeric columns once so filtering is fast
    df["rate"] = pd.to_numeric(
        df["rate"].astype(str).str.extract(r"(\d+\.\d+|\d+)")[0], errors="coerce"
    )
    if "approx_cost(for_two_people)" in df.columns:
        df["approx_cost(for_two_people)"] = pd.to_numeric(
            df["approx_cost(for_two_people)"].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        )
    return df

@st.cache_data(show_spinner=False)
def get_locations(df: pd.DataFrame):
    if df.empty:
        return []
    locs = sorted(
        str(x) for x in df["location"].dropna().unique()
        if str(x).strip() and str(x) != "Unknown"
    )
    return locs

@st.cache_data(show_spinner=False)
def get_cuisine_list(df: pd.DataFrame):
    if df.empty:
        return []
    cuisines: set = set()
    for row in df["cuisines"].dropna():
        for c in str(row).split(","):
            c = c.strip()
            if c and c != "Unknown":
                cuisines.add(c)
    return sorted(cuisines)

# ── Ensure dataset is on disk (download if needed), then load ────────────────
# _ensure_dataset_exists() must run OUTSIDE @st.cache_data so st.spinner works.
if "_dataset_ready" not in st.session_state:
    st.session_state["_dataset_ready"] = _ensure_dataset_exists()

if not st.session_state["_dataset_ready"]:
    st.stop()

df = load_data()
ALL_LOCATIONS = get_locations(df)
ALL_CUISINES  = get_cuisine_list(df)

# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar — Preference Filters
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔎 Your Preferences")
    st.caption("Narrow your search — leave any field blank for no restriction.")
    st.divider()

    # Location
    location_opts = ["Any area in Bangalore"] + ALL_LOCATIONS
    selected_loc = st.selectbox("📍 Location", location_opts, index=0)
    location = None if selected_loc == "Any area in Bangalore" else selected_loc

    # Budget
    budget_max = st.slider(
        "💰 Max Budget (₹ for two people)",
        min_value=100, max_value=3000, value=1000, step=50,
        help="Restaurants with cost-for-two above this will be excluded."
    )

    # Minimum rating
    min_rating = st.slider(
        "⭐ Minimum Rating",
        min_value=1.0, max_value=5.0, value=4.0, step=0.1,
        format="%.1f"
    )

    # Cuisines
    selected_cuisines = st.multiselect(
        "🍽️ Cuisine Preferences",
        options=ALL_CUISINES,
        default=[],
        placeholder="Any cuisine — leave empty for all",
    )

    # Custom vibe (passed to LLM context)
    custom_pref = st.text_area(
        "✨ Vibe & Extra Preferences",
        placeholder="e.g. rooftop seating, family-friendly, quiet atmosphere, vegan-friendly…",
        height=80,
    )

    st.divider()
    find_btn = st.button("🤖  Find My Restaurants", type="primary")

    st.markdown("---")
    st.caption(
        "Powered by **Groq · Llama-3.1** + Zomato dataset  \n"
        "© 2024 Zomato AI · Phase 7 Streamlit"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════════
col_brand, col_meta = st.columns([4, 1])
with col_brand:
    st.markdown(
        '<span class="brand">Zomato AI</span>'
        '<span class="brand-badge">AI</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "#### Discover Bangalore's best restaurants, curated by an AI food critic."
    )

if df.empty:
    st.error(
        "⚠️ Dataset loaded but appears empty — the CSV may be corrupt. "
        "Try clearing the cache or re-deploying."
    )
    st.stop()

with col_meta:
    st.metric("Restaurants in DB", f"{len(df):,}")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# Main logic — runs when button is clicked
# ═══════════════════════════════════════════════════════════════════════════════
if find_btn:
    # ── 1. Build preferences ──────────────────────────────────────────────────
    prefs = UserPreferences(
        location=location,
        budget_max=float(budget_max),
        cuisines=selected_cuisines if selected_cuisines else None,
        min_rating=float(min_rating),
    )

    prefs_dict = {
        "Location":         location or "Any",
        "Budget (Max ₹)":   budget_max,
        "Cuisines":         selected_cuisines or "Any",
        "Min Rating":       min_rating,
        "Custom Vibe":      custom_pref or "None",
    }

    # ── 2. Filter engine ──────────────────────────────────────────────────────
    with st.status("🔍 Scanning the database…", expanded=False) as status:
        t0 = time.perf_counter()
        filtered_df = filter_restaurants(df, prefs, top_k=15)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        status.update(
            label=f"✅ Scanned {len(df):,} restaurants in {elapsed_ms:.0f} ms — "
                  f"**{len(filtered_df)}** candidates shortlisted",
            state="complete",
        )

    if filtered_df.empty:
        st.markdown(
            '<div class="empty">'
            '<h3>😔 No restaurants matched your criteria</h3>'
            "<p>Try broadening your filters — lower the minimum rating, "
            "increase the budget, or remove some cuisine preferences.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.stop()

    # ── 3. Groq LLM ───────────────────────────────────────────────────────────
    # Resolve API key: prefer Streamlit secrets, fall back to .env
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
        os.environ["GROQ_API_KEY"] = groq_key
    except (KeyError, FileNotFoundError):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))

    with st.status("🤖 AI Food Critic is reviewing menus…", expanded=False) as status:
        try:
            t1 = time.perf_counter()
            recommendations = get_recommendations(filtered_df, prefs_dict)
            llm_ms = (time.perf_counter() - t1) * 1000
            status.update(
                label=f"✅ AI ranked **{len(recommendations)}** top picks in {llm_ms:.0f} ms",
                state="complete",
            )
        except Exception as e:
            status.update(label="❌ LLM call failed", state="error")
            st.error(f"Groq API error: {e}")
            st.stop()

    if not recommendations:
        st.warning("The LLM returned no recommendations. Try different filters.")
        st.stop()

    # ── 4. Render results ─────────────────────────────────────────────────────
    summary_parts = []
    if location:       summary_parts.append(f"📍 {location}")
    if selected_cuisines: summary_parts.append("🍽️ " + ", ".join(selected_cuisines))
    summary_parts.append(f"💰 Under ₹{budget_max}")
    summary_parts.append(f"⭐ {min_rating}+")

    st.success(
        f"**{len(recommendations)} AI Recommendations** for: "
        + "  ·  ".join(summary_parts)
    )

    # Responsive 2-column grid
    cols = st.columns(2)
    for i, rec in enumerate(recommendations):
        name      = rec.get("name", "Unknown")
        cuisine   = rec.get("cuisine", "—")
        rating    = rec.get("rating", "N/A")
        cost      = rec.get("cost", "N/A")
        reasoning = rec.get("reasoning", "")

        # Build star string
        try:
            stars_n = round(float(rating))
            stars   = "★" * stars_n + "☆" * (5 - stars_n)
        except (TypeError, ValueError):
            stars = "—"

        cost_str  = f"₹{cost}" if cost not in ("N/A", None, "") else "N/A"

        card_html = f"""
        <div class="rest-card">
            <div style="display:flex; align-items:center; margin-bottom:10px;">
                <span class="rank">{i + 1}</span>
                <span style="font-size:1.15rem; font-weight:700; font-family:'Plus Jakarta Sans',sans-serif;">
                    {name}
                </span>
            </div>

            <span class="pill pill-primary">{stars} {rating}</span>
            <span class="pill">{cost_str}</span>
            <span class="pill">🍴 {cuisine}</span>

            <div class="reasoning">
                <span class="ai-chip">✦ AI Reasoning</span><br/><br/>
                "{reasoning}"
            </div>
        </div>
        """
        with cols[i % 2]:
            st.markdown(card_html, unsafe_allow_html=True)

    # ── 5. Raw data expander ──────────────────────────────────────────────────
    with st.expander("🔬 View shortlisted candidates (pre-LLM filter)", expanded=False):
        display_cols = ["name", "location", "cuisines", "rate",
                        "approx_cost(for_two_people)", "dish_liked"]
        avail = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(
            filtered_df[avail].rename(columns={
                "approx_cost(for_two_people)": "cost_for_two",
                "dish_liked": "popular_dishes",
            }).reset_index(drop=True),
            use_container_width=True,
        )

# ── Default state (no search yet) ────────────────────────────────────────────
else:
    st.markdown(
        '<div class="empty">'
        '<h3>👈 Set your preferences and click <em>Find My Restaurants</em></h3>'
        "<p>The AI food critic will scan <strong>{:,}</strong> Bangalore restaurants "
        "and hand-pick the best matches for you.</p>"
        "</div>".format(len(df)),
        unsafe_allow_html=True,
    )
