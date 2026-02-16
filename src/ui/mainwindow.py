from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QMessageBox, QLabel)
from PyQt6.QtCore import QThread
import os
from src.core.db import DatabaseHandler
from src.core.http_client import HttpClient
from src.core.downloader import DownloadManager
from src.ui.browser import FileBrowser
from src.ui.player import PlayerWidget
from src.ui.downloads import DownloadsWidget

class IndexerThread(QThread):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        self.client.scan_server()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DhakaFlix Streamer")
        self.resize(1200, 800)
        
        # Core Components
        self.db = DatabaseHandler()
        self.client = HttpClient()
        self.downloader = DownloadManager(download_dir=os.path.join(os.getcwd(), "downloads"))
        
        # Threading for Indexer
        self.indexer_thread = IndexerThread(self.client)
        self.client.progress_signal.connect(self.update_status)
        self.client.file_found_signal.connect(self.on_file_found)
        self.client.finished_signal.connect(self.on_scan_finished)
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_sidebar()
        self.setup_content_area()
        
        # Initial Status
        self.status_label.setText("Ready. Click 'Update Index' to scan server.")

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2b2b2b; color: white;")
        layout = QVBoxLayout(self.sidebar)
        
        # Buttons
        self.btn_browser = QPushButton("Browser")
        self.btn_browser.clicked.connect(lambda: self.switch_view(0))
        layout.addWidget(self.btn_browser)
        
        self.btn_downloads = QPushButton("Downloads")
        self.btn_downloads.clicked.connect(lambda: self.switch_view(2))
        layout.addWidget(self.btn_downloads)
        
        self.btn_update = QPushButton("Update Index")
        self.btn_update.clicked.connect(self.start_indexing)
        layout.addWidget(self.btn_update)
        
        layout.addStretch()
        
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.sidebar)

    def setup_content_area(self):
        self.stack = QStackedWidget()
        
        # View 0: Browser
        self.browser = FileBrowser(self.db)
        self.browser.file_selected.connect(self.play_file)
        self.browser.download_requested.connect(self.start_download)
        self.stack.addWidget(self.browser)
        
        # View 1: Player
        self.player = PlayerWidget()
        self.stack.addWidget(self.player)
        
        # View 2: Downloads
        self.downloads_ui = DownloadsWidget()
        self.stack.addWidget(self.downloads_ui)
        
        self.main_layout.addWidget(self.stack)

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)
        if index != 1:
            self.player.stop()

    def start_indexing(self):
        if self.indexer_thread.isRunning():
            return
        
        reply = QMessageBox.question(self, "Full Rescan", 
                                     "This will re-scan the entire server (172.16.50.9). It may take a while.\nContinue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # self.db.clear_index() # Keep additive for now, or uncomment to wipe first
            self.indexer_thread.start()
            self.btn_update.setEnabled(False)
            self.status_label.setText("Scanning server... Please wait.")

    def update_status(self, msg):
        self.status_label.setText(msg)

    def on_file_found(self, data):
        self.db.add_file(data['path'], data['filename'], data['parent_dir'])

    def on_scan_finished(self):
        self.db.commit()
        self.status_label.setText("Indexing Complete!")
        self.btn_update.setEnabled(True)
        self.browser.load_files() # Refresh view with new files

    def play_file(self, path):
        self.switch_view(1)
        self.player.play(path)

    def start_download(self, url, filename):
        self.switch_view(2) # Switch to downloads view
        worker = self.downloader.start_download(url, filename)
        if worker:
            self.downloads_ui.add_download(url, filename)
            worker.progress.connect(lambda url, pct: self.downloads_ui.update_progress(url, pct))
            worker.finished.connect(self.on_download_finished)

    def on_download_finished(self, url, path):
        self.downloads_ui.mark_completed(url)
        self.db.mark_downloaded(url, path)
        QMessageBox.information(self, "Download Complete", f"Downloaded {os.path.basename(path)}")

    def closeEvent(self, event):
        self.client.stop()
        if self.indexer_thread.isRunning():
            self.indexer_thread.wait()
        self.db.close()
        self.player.terminate()
        event.accept()
