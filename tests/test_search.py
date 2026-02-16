import sys
import os
import unittest

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.core.db import DatabaseHandler

class TestSearch(unittest.TestCase):
    def setUp(self):
        # Use in-memory DB for testing
        self.db = DatabaseHandler(":memory:")
        self.db.init_db()
        
        # Populate with mock data
        self.db.add_file("http://172.16.50.9/Movies/2001_A_Space_Odyssey.mkv", "2001: A Space Odyssey.mkv", "Movies")
        self.db.add_file("http://172.16.50.9/Anime/One_Piece.mkv", "One Piece.mkv", "Anime")
        self.db.commit()

    def test_search_space_odyssey(self):
        print("\nTesting search for 'A space odyssey'...")
        results = self.db.search("A space odyssey")
        
        found = False
        for path, filename, category in results:
            print(f"Found: {filename}")
            if "Space Odyssey" in filename:
                found = True
        
        self.assertTrue(found, "Search failed to find 'A Space Odyssey'")
        print("Test Passed: Found 'A Space Odyssey'")

    def tearDown(self):
        self.db.close()

if __name__ == "__main__":
    unittest.main()
