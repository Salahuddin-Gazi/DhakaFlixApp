import sys
import os
import shutil
import time
from PyQt6.QtCore import QCoreApplication

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.core.db import DatabaseHandler
from src.core.downloader import DownloadManager

def run_test():
    app = QCoreApplication(sys.argv)
    
    # 1. Setup Environment
    download_dir = os.path.join(parent_dir, "tests", "downloads_ultimate")
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)
    
    db = DatabaseHandler(":memory:") # Use fresh in-memory DB
    db.init_db()
    
    manager = DownloadManager(download_dir)
    
    target_filename = "2001_A_Space_Odyssey.mkv"
    target_url = f"http://localhost:8001/DHAKA-FLIX-9/Movies/{target_filename}"
    
    print("\n--- PHASE 1: Indexing ---")
    # Simulate finding the file via scanning
    print(f"Indexing {target_filename}...")
    db.add_file(target_url, "2001: A Space Odyssey", "Movies")
    db.commit()
    
    print("\n--- PHASE 2: Search ---")
    query = "A space odyssey"
    print(f"Searching for '{query}'...")
    results = db.search(query)
    
    found_item = None
    for res in results:
        # path, filename, category, local_path, downloaded
        # 0     1         2         3           4
        if "Space Odyssey" in res[1]:
            found_item = res
            print(f"FOUND: {res[1]} at {res[0]}")
            break
            
    if not found_item:
        print("TEST FAILED: Search did not find the file.")
        sys.exit(1)
        
    print("\n--- PHASE 3: Download ---")
    download_url = found_item[0]
    print(f"Downloading from {download_url}...")
    
    def on_finished(url, path):
        print(f"Download finished: {path}")
        
        # Verify File Logic
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("File verified on disk.")
            
            # Update DB like the app does
            db.mark_downloaded(url, path)
            
            # Verify "Play" Logic (getting local path)
            print("\n--- PHASE 4: Play (Verification) ---")
            local_play_path = db.get_local_path(url)
            
            if local_play_path == path:
                 print(f"Player would open local file: {local_play_path}")
                 print("TEST PASSED: Full flow verified!")
                 sys.exit(0)
            else:
                print(f"TEST FAILED: DB did not return local path. Got: {local_play_path}")
                sys.exit(1)
        else:
            print("TEST FAILED: File missing or empty.")
            sys.exit(1)

    def on_error(url, msg):
        print(f"TEST FAILED: Download Error {msg}")
        sys.exit(1)

    worker = manager.start_download(download_url, target_filename)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    
    app.exec()

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        sys.exit(1)
