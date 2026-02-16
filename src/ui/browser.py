import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                             QLineEdit, QPushButton, QHBoxLayout, QListWidgetItem, QMenu)
from PyQt6.QtCore import pyqtSignal, Qt

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
        self.search_bar.textChanged.connect(self.search_files)
        self.layout.addWidget(self.search_bar)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_item_double_click)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.layout.addWidget(self.file_list)
        
        # Initial Load
        self.load_files()

    def load_files(self):
        self.file_list.clear() 
        results = self.db.search("") # Empty query = get recent/all (limited by DB method)
        for path, filename, category, local_path, downloaded in results:
            display_text = f"{filename} ({category})"
            if downloaded:
                display_text = f"[OFFLINE] {display_text}"
            
            item = QListWidgetItem(display_text)
            item.setData(100, path)
            item.setData(101, filename)
            item.setData(102, local_path if downloaded else None)
            self.file_list.addItem(item)

    def search_files(self, text):
        if len(text) < 3:
            return
            
        self.file_list.clear()
        results = self.db.search(text)
        for path, filename, category, local_path, downloaded in results:
            display_text = f"{filename} ({category})"
            if downloaded:
                display_text = f"[OFFLINE] {display_text}"
            
            item = QListWidgetItem(display_text)
            item.setData(100, path) # URL
            item.setData(101, filename)
            item.setData(102, local_path if downloaded else None)
            self.file_list.addItem(item)

    def on_item_double_click(self, item):
        url = item.data(100)
        local_path = item.data(102)
        
        # Play local file if available, else stream URL
        if local_path and os.path.exists(local_path):
            self.file_selected.emit(local_path)
        else:
            self.file_selected.emit(url)

    def open_context_menu(self, position):
        item = self.file_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        download_action = menu.addAction("Download")
        action = menu.exec(self.file_list.mapToGlobal(position))
        
        if action == download_action:
            url = item.data(100)
            filename = item.data(101)
            self.download_requested.emit(url, filename)

