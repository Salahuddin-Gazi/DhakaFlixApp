import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.core.db import DatabaseHandler
from src.ui.browser import FileBrowser

def run_test():
    app = QApplication(sys.argv)
    
    # 1. Setup DB with data
    db_path = os.path.join(parent_dir, "tests", "test_persistence.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = DatabaseHandler(db_path)
    db.init_db()
    db.add_file("http://example.com/file1.mkv", "Persisted File 1.mkv", "Movies")
    db.add_file("http://example.com/file2.mkv", "Persisted File 2.mkv", "Anime")
    db.commit()
    
    # 2. Create Browser (simulating app restart)
    print("Creating Browser with existing DB...")
    browser = FileBrowser(db)
    
    # 3. Verify items loaded
    count = browser.file_list.count()
    print(f"Browser loaded {count} items.")
    
    if count == 2:
        item1 = browser.file_list.item(0).text()
        print(f"Item 1: {item1}")
        if "Persisted File" in item1:
             print("TEST PASSED: Data persisted and loaded on startup.")
             sys.exit(0)
    
    print("TEST FAILED: Browser did not load persisted data.")
    sys.exit(1)

if __name__ == "__main__":
    run_test()
