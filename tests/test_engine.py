import sys
import os
import pandas as pd
import unittest

# Add src to path so we can import engine
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from engine.filter import filter_restaurants, UserPreferences

class TestFilteringEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the processed dataset
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "processed_zomato.csv")
        try:
            cls.df = pd.read_csv(data_path)
        except Exception as e:
            print(f"Failed to load dataset: {e}")
            cls.df = pd.DataFrame()

    def test_filter_by_location(self):
        if self.df.empty:
            self.skipTest("No data available")
        prefs = UserPreferences(location="Banashankari")
        res = filter_restaurants(self.df, prefs)
        self.assertTrue(all(res['location'].str.contains('Banashankari', case=False) | res['listed_in(city)'].str.contains('Banashankari', case=False)))

    def test_filter_by_cuisine_and_rating(self):
        if self.df.empty:
            self.skipTest("No data available")
        prefs = UserPreferences(cuisines=["Italian"], min_rating=4.5)
        res = filter_restaurants(self.df, prefs)
        self.assertTrue(all(res['cuisines'].str.contains('Italian', case=False)))
        self.assertTrue(all(res['rate'] >= 4.5))

    def test_top_k_limit(self):
        if self.df.empty:
            self.skipTest("No data available")
        prefs = UserPreferences(location="Indiranagar")
        res = filter_restaurants(self.df, prefs, top_k=5)
        self.assertLessEqual(len(res), 5)

if __name__ == "__main__":
    unittest.main()
