import sys
import os
import time
import shutil
from PyQt6.QtCore import QCoreApplication

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.core.downloader import DownloadManager

def run_test():
    app = QCoreApplication(sys.argv)
    
    download_dir = os.path.join(parent_dir, "tests", "downloads")
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)
    
    manager = DownloadManager(download_dir)
    
    url = "http://localhost:8001/DHAKA-FLIX-9/video.mp4"
    filename = "video.mp4"
    
    print(f"Starting download of {url}...")
    sys.stdout.flush()
    
    def on_finished(url, path):
        print(f"Download finished: {path}")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("TEST PASSED: File downloaded successfully.")
        else:
            print("TEST FAILED: File missing or empty.")
        sys.stdout.flush()
        sys.exit(0)

    def on_error(url, msg):
        print(f"TEST FAILED: Error {msg}")
        sys.stdout.flush()
        sys.exit(1)

    worker = manager.start_download(url, filename)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    
    app.exec()

if __name__ == "__main__":
    run_test()
