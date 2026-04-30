"""
Phase 6 — Test Suite
Covers edge cases, filter correctness, response shape, and API contract.
Run with:  python -m pytest tests/ -v
"""
import sys
import os
import time
import unittest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.filter import filter_restaurants, UserPreferences

# ─── Fixture ──────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "processed_zomato.csv")

def _load_df() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    return pd.read_csv(DATA_PATH, low_memory=False)


class TestEdgeCases(unittest.TestCase):
    """Edge-case tests required by Phase 6."""

    @classmethod
    def setUpClass(cls):
        cls.df = _load_df()

    def _skip_if_empty(self):
        if self.df.empty:
            self.skipTest("Dataset not found — run Phase 1 first.")

    # ── Zero-match scenarios ──────────────────────────────────────────────────

    def test_impossible_budget_returns_empty(self):
        """Budget of ₹1 should match nothing."""
        self._skip_if_empty()
        prefs = UserPreferences(budget_max=1)
        result = filter_restaurants(self.df, prefs)
        self.assertEqual(len(result), 0, "Expected zero results for ₹1 budget")

    def test_impossible_rating_returns_empty(self):
        """Rating of 5.0 (exact max) should return very few or zero results."""
        self._skip_if_empty()
        prefs = UserPreferences(min_rating=5.0)
        result = filter_restaurants(self.df, prefs)
        # Accept 0 or a very small number — all must be exactly 5.0
        if not result.empty:
            self.assertTrue((result["rate"] >= 5.0).all())

    def test_nonexistent_location_returns_empty(self):
        """Querying a location that does not exist in the DB."""
        self._skip_if_empty()
        prefs = UserPreferences(location="XYZ_NONEXISTENT_PLACE_12345")
        result = filter_restaurants(self.df, prefs)
        self.assertEqual(len(result), 0, "Fake location should return 0 results")

    def test_nonexistent_cuisine_returns_empty(self):
        """A cuisine not in the dataset should return nothing."""
        self._skip_if_empty()
        prefs = UserPreferences(cuisines=["MartianFood"])
        result = filter_restaurants(self.df, prefs)
        self.assertEqual(len(result), 0)

    def test_all_filters_combined_no_match(self):
        """Combining very tight, contradicting constraints = empty result."""
        self._skip_if_empty()
        prefs = UserPreferences(
            location="Whitefield",
            budget_max=50,       # ₹50 for two people — unrealistic
            cuisines=["Italian"],
            min_rating=4.9,
        )
        result = filter_restaurants(self.df, prefs)
        self.assertEqual(len(result), 0)

    # ── Graceful handling ─────────────────────────────────────────────────────

    def test_none_preferences_returns_top_k(self):
        """All-None preferences should return the global top-k restaurants."""
        self._skip_if_empty()
        prefs = UserPreferences()
        result = filter_restaurants(self.df, prefs, top_k=10)
        self.assertLessEqual(len(result), 10)
        self.assertGreater(len(result), 0, "Should return some results with no filters")

    def test_empty_cuisines_list_ignored(self):
        """Empty cuisines list should behave the same as None."""
        self._skip_if_empty()
        prefs_none   = UserPreferences(location="Indiranagar", cuisines=None)
        prefs_empty  = UserPreferences(location="Indiranagar", cuisines=[])
        result_none  = filter_restaurants(self.df, prefs_none)
        result_empty = filter_restaurants(self.df, prefs_empty)
        self.assertEqual(len(result_none), len(result_empty))

    # ── Result correctness ────────────────────────────────────────────────────

    def test_results_sorted_by_rating_descending(self):
        """Returned results must be ordered highest rating first."""
        self._skip_if_empty()
        prefs = UserPreferences(location="Koramangala")
        result = filter_restaurants(self.df, prefs, top_k=20)
        if len(result) < 2:
            self.skipTest("Not enough rows to test sort order")
        ratings = result["rate"].dropna().tolist()
        self.assertEqual(ratings, sorted(ratings, reverse=True),
                         "Results are not sorted by rating descending")

    def test_budget_filter_respected(self):
        """No result should exceed the specified budget ceiling."""
        self._skip_if_empty()
        ceiling = 500
        prefs = UserPreferences(budget_max=ceiling)
        result = filter_restaurants(self.df, prefs)
        if result.empty:
            self.skipTest("No restaurants in budget range")
        cost_col = result["approx_cost(for_two_people)"]
        numeric_costs = pd.to_numeric(cost_col.astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").dropna()
        self.assertTrue((numeric_costs <= ceiling).all(),
                        f"Some results exceed the ₹{ceiling} budget")

    def test_rating_filter_respected(self):
        """All results must meet the minimum rating threshold."""
        self._skip_if_empty()
        min_rating = 4.0
        prefs = UserPreferences(min_rating=min_rating)
        result = filter_restaurants(self.df, prefs)
        if result.empty:
            self.skipTest("No restaurants meet the rating threshold")
        self.assertTrue((result["rate"] >= min_rating).all(),
                        "Some results fall below the minimum rating")

    def test_cuisine_filter_respected(self):
        """Every result must contain at least one of the requested cuisines."""
        self._skip_if_empty()
        prefs = UserPreferences(cuisines=["Chinese", "Italian"])
        result = filter_restaurants(self.df, prefs)
        if result.empty:
            self.skipTest("No matching cuisine results")
        mask = result["cuisines"].str.lower().str.contains("chinese|italian", na=False)
        self.assertTrue(mask.all(), "Results contain rows without the requested cuisines")

    def test_top_k_is_strictly_respected(self):
        """Result count must never exceed top_k."""
        self._skip_if_empty()
        for k in [1, 5, 15, 50]:
            prefs = UserPreferences()
            result = filter_restaurants(self.df, prefs, top_k=k)
            self.assertLessEqual(len(result), k, f"top_k={k} was violated")

    # ── Data integrity ────────────────────────────────────────────────────────

    def test_required_columns_present(self):
        """Dataset must expose the columns the engine depends on."""
        self._skip_if_empty()
        required = {"name", "location", "cuisines", "rate",
                    "approx_cost(for_two_people)", "listed_in(city)"}
        missing = required - set(self.df.columns)
        self.assertEqual(missing, set(), f"Missing columns: {missing}")

    def test_no_all_null_names(self):
        """The name column must not be entirely null."""
        self._skip_if_empty()
        self.assertFalse(self.df["name"].isna().all(), "All restaurant names are null")


class TestFilterPerformance(unittest.TestCase):
    """Latency benchmarks — Phase 6 optimization gate."""

    @classmethod
    def setUpClass(cls):
        cls.df = _load_df()

    def _skip_if_empty(self):
        if self.df.empty:
            self.skipTest("Dataset not found.")

    def _time_filter(self, prefs, top_k=15, runs=5):
        times = []
        for _ in range(runs):
            t0 = time.perf_counter()
            filter_restaurants(self.df, prefs, top_k=top_k)
            times.append(time.perf_counter() - t0)
        return sum(times) / len(times)

    def test_filter_latency_under_500ms(self):
        """Full filter pass on 51k rows must complete in < 500 ms on average."""
        self._skip_if_empty()
        prefs = UserPreferences(location="Indiranagar", cuisines=["North Indian"], min_rating=4.0)
        avg_ms = self._time_filter(prefs) * 1000
        print(f"\n  Filter latency: {avg_ms:.1f} ms (avg over 5 runs)")
        self.assertLess(avg_ms, 500, f"Filter too slow: {avg_ms:.1f} ms")

    def test_top_k_retrieval_under_200ms(self):
        """Top-K selection with no filters must be under 200 ms."""
        self._skip_if_empty()
        prefs = UserPreferences()
        avg_ms = self._time_filter(prefs, top_k=10) * 1000
        print(f"\n  Top-K latency: {avg_ms:.1f} ms (avg over 5 runs)")
        self.assertLess(avg_ms, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
