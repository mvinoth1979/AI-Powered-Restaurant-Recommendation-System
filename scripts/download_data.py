"""
scripts/download_data.py
────────────────────────
Downloads and processes the Zomato restaurant dataset from Hugging Face.
Run this ONCE after cloning the repo:

    python scripts/download_data.py

The processed CSV is excluded from git (547 MB > GitHub 100 MB limit).
This script regenerates it in: data/processed/processed_zomato.csv
"""

import os
import sys
import pandas as pd

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "processed", "processed_zomato.csv"
)

def download_and_process():
    print("=" * 60)
    print("Zomato AI — Data Download Script")
    print("=" * 60)

    # ── Check if already exists ───────────────────────────────────────────────
    if os.path.exists(OUTPUT_PATH):
        size_mb = os.path.getsize(OUTPUT_PATH) / 1e6
        print(f"\n✅ Dataset already exists ({size_mb:.0f} MB):")
        print(f"   {OUTPUT_PATH}")
        print("\nDelete the file and re-run this script to force a fresh download.")
        return

    # ── Install datasets library if missing ───────────────────────────────────
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n📦 Installing 'datasets' library…")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets"])
        from datasets import load_dataset

    # ── Download from Hugging Face ────────────────────────────────────────────
    print("\n⬇  Downloading from Hugging Face:")
    print("   ManikaSaini/zomato-restaurant-recommendation")
    print("   (this may take a few minutes on first run)\n")

    dataset = load_dataset(
        "ManikaSaini/zomato-restaurant-recommendation",
        trust_remote_code=True,
    )

    # ── Convert to DataFrame ──────────────────────────────────────────────────
    df = dataset["train"].to_pandas()
    print(f"   Downloaded {len(df):,} rows, {len(df.columns)} columns.")

    # ── Clean & process ───────────────────────────────────────────────────────
    print("\n🔧 Processing…")

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop fully-null columns
    df.dropna(how="all", axis=1, inplace=True)

    # Standardise key columns
    if "rate" in df.columns:
        df["rate"] = (
            df["rate"].astype(str)
            .str.extract(r"(\d+\.\d+|\d+)")[0]
        )
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    if "approx_cost(for_two_people)" in df.columns:
        df["approx_cost(for_two_people)"] = (
            df["approx_cost(for_two_people)"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        df["approx_cost(for_two_people)"] = pd.to_numeric(
            df["approx_cost(for_two_people)"], errors="coerce"
        )

    if "votes" in df.columns:
        df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)

    if "location" in df.columns:
        df["location"] = df["location"].astype(str).str.strip()

    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].astype(str).str.strip()

    print(f"   After cleaning: {len(df):,} rows retained.")

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    size_mb = os.path.getsize(OUTPUT_PATH) / 1e6

    print(f"\n✅ Saved to: {OUTPUT_PATH}")
    print(f"   Size: {size_mb:.1f} MB  |  Rows: {len(df):,}")
    print("\nYou can now run the app:")
    print("  Backend : python -m uvicorn src.api.main:app --port 8000")
    print("  Frontend: cd frontend && npm run dev")
    print("  Streamlit: streamlit run src/ui/streamlit_app.py")


if __name__ == "__main__":
    download_and_process()
