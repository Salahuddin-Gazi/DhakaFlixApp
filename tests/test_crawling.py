import sys
import os
import time

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt6.QtCore import QCoreApplication
from src.core.http_client import HttpClient

def run_test():
    app = QCoreApplication(sys.argv)
    
    # Point to local mock server
    client = HttpClient(base_url="http://127.0.0.1:8001/DHAKA-FLIX-9/") # Port 8001
    
    found_files = []
    
    def on_file_found(data):
        print(f"Found: {data['filename']}")
        found_files.append(data)

    def on_finished():
        print(f"Scan finished. Found {len(found_files)} files.")
        if len(found_files) >= 2:
            print("TEST PASSED: Found expected files.")
            sys.exit(0)
        else:
            print(f"TEST FAILED: Found {len(found_files)} files, expected at least 2.")
            sys.exit(1)

    client.file_found_signal.connect(on_file_found)
    client.finished_signal.connect(on_finished)
    
    print("Starting crawl...")
    client.scan_server()
    
    app.exec()

if __name__ == "__main__":
    run_test()
