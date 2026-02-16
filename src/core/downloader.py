import os
import requests
from PyQt6.QtCore import QThread, pyqtSignal, QObject

class DownloadWorker(QThread):
    progress = pyqtSignal(str, float) # url, percentage
    finished = pyqtSignal(str, str) # url, local_path
    error = pyqtSignal(str, str) # url, error_msg

    def __init__(self, url, dest_path):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        self.is_cancelled = False

    def run(self):
        try:
            os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
            response = requests.get(self.url, stream=True, timeout=10)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.is_cancelled:
                        break
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.progress.emit(self.url, percent)
            
            if not self.is_cancelled:
                self.finished.emit(self.url, self.dest_path)
            else:
                os.remove(self.dest_path) # Cleanup partial
                
        except Exception as e:
            self.error.emit(self.url, str(e))

class DownloadManager(QObject):
    def __init__(self, download_dir):
        super().__init__()
        self.download_dir = download_dir
        self.active_downloads = {} # url -> worker

    def start_download(self, url, filename):
        if url in self.active_downloads:
            return # Already downloading

        dest_path = os.path.join(self.download_dir, filename)
        worker = DownloadWorker(url, dest_path)
        worker.progress.connect(self.print_progress) # Placeholder for now
        worker.finished.connect(self.on_finished)
        worker.error.connect(self.on_error)
        
        self.active_downloads[url] = worker
        worker.start()
        return worker

    def cancel_download(self, url):
        if url in self.active_downloads:
            self.active_downloads[url].is_cancelled = True
            self.active_downloads[url].wait()
            del self.active_downloads[url]

    def print_progress(self, url, percent):
        print(f"Downloading {url}: {percent:.1f}%")

    def on_finished(self, url, path):
        print(f"Download complete: {path}")
        if url in self.active_downloads:
            del self.active_downloads[url]

    def on_error(self, url, msg):
        print(f"Download error {url}: {msg}")
        if url in self.active_downloads:
            del self.active_downloads[url]
