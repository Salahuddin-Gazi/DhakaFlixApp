import os
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QLabel, QMenu, QMessageBox, 
                             QTreeWidget, QTreeWidgetItem, QTabWidget, QTreeWidgetItemIterator)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, QTimer

class SearchThread(QThread):
    results_ready = pyqtSignal(list)
    
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.query = ""
        
    def search(self, query):
        self.query = query
        self.start()
        
    def run(self):
        results = self.db.search(self.query)
        self.results_ready.emit(results)

class FileBrowser(QWidget):
    file_selected = pyqtSignal(str) # Emits file path
    download_requested = pyqtSignal(str, str) # url, filename
    
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.layout = QVBoxLayout(self)
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        self.layout.addWidget(self.search_bar)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_item_double_click)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.layout.addWidget(self.file_list)
        
        # Threading & Debounce
        self.search_thread = SearchThread(self.db)
        self.search_thread.results_ready.connect(self.on_search_results)
        
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(300) # 300ms delay
        self.debounce_timer.timeout.connect(self.perform_search)
        
        # Initial Load
        self.load_files()

    def load_files(self):
        self.perform_search(force_empty=True)

    def on_search_text_changed(self, text):
        self.debounce_timer.start()

    def perform_search(self, force_empty=False):
        query = "" if force_empty else self.search_bar.text()
        if len(query) > 0 and len(query) < 3:
            return # Skip short queries unless empty (which means load all/recent)
        
        self.search_thread.search(query)

    def on_search_results(self, results):
        self.file_list.clear()
        
        if not results:
            item = QListWidgetItem("No results found")
            item.setFlags(Qt.ItemFlag.NoItemFlags) # Make unselectable
            self.file_list.addItem(item)
            return

        for path, filename, category, local_path, downloaded in results:
            display_text = f"{filename} ({category})"
            if downloaded:
                display_text = f"[OFFLINE] {display_text}"
            
            item = QListWidgetItem(display_text)
            item.setData(100, path)
            item.setData(101, filename)
            item.setData(102, local_path if downloaded else None)
            self.file_list.addItem(item)

    def on_item_double_click(self, item):
        url = item.data(100)
        
        if not url: # Handle "No results found" or invalid items
            return
            
        local_path = item.data(102)
        
        # Play local file if available, else stream URL
        if local_path:
            if os.path.exists(local_path):
                self.file_selected.emit(local_path)
            else:
                # Fallback to stream if local file missing
                QMessageBox.warning(self, "File Missing", "Local file not found. Streaming from server instead.")
                self.file_selected.emit(url)
        else:
            self.file_selected.emit(url)

    def open_context_menu(self, position):
        item = self.file_list.itemAt(position)
        if not item:
            return
            
        url = item.data(100)
        if not url: # Ignore "No results found"
            return
            
        menu = QMenu()
        download_action = menu.addAction("Download")
        
        action = menu.exec(self.file_list.mapToGlobal(position))
        
    def get_current_items(self):
        """Returns a list of (url, local_path) tuples from the current view."""
        items = []
        if self.tabs.currentIndex() == 0: # List View
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                    items.append((item.data(100), item.data(102)))
        else: # Tree View
             iterator = QTreeWidgetItemIterator(self.file_tree)
             while iterator.value():
                 item = iterator.value()
                 url = item.data(0, Qt.ItemDataRole.UserRole)
                 if url:
                     # Check DB for local path as tree doesn't store it yet (optimization later)
                     local_path = self.db.get_local_path(url)
                     items.append((url, local_path))
                 iterator += 1
        return items

    def get_next_file(self, current_path):
        items = self.get_current_items()
        for i, (url, local_path) in enumerate(items):
            # Check matches for both URL or Local Path (as current_path could be either)
            if url == current_path or local_path == current_path:
                if i + 1 < len(items):
                    return items[i+1][1] if items[i+1][1] and os.path.exists(items[i+1][1]) else items[i+1][0]
        return None

    def get_prev_file(self, current_path):
        items = self.get_current_items()
        for i, (url, local_path) in enumerate(items):
            if url == current_path or local_path == current_path:
                if i - 1 >= 0:
                     return items[i-1][1] if items[i-1][1] and os.path.exists(items[i-1][1]) else items[i-1][0]
        return None

