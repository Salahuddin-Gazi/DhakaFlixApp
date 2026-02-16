import os
import time
import urllib.parse
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
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # --- Tab 1: Search ---
        self.search_widget = QWidget()
        search_layout = QVBoxLayout(self.search_widget)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_bar)
        
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_item_double_click)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        search_layout.addWidget(self.file_list)
        
        self.tabs.addTab(self.search_widget, "Search")
        
        # --- Tab 2: Browse (Tree) ---
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        
        self.tree_search_bar = QLineEdit()
        self.tree_search_bar.setPlaceholderText("Filter folders/files...")
        self.tree_search_bar.textChanged.connect(self.filter_tree)
        tree_layout.addWidget(self.tree_search_bar)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type"])
        self.file_tree.setColumnWidth(0, 400)
        self.file_tree.itemDoubleClicked.connect(self.on_tree_item_double_click)
        tree_layout.addWidget(self.file_tree)
        
        self.tabs.addTab(self.tree_widget, "Browse")
        
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
        self.load_tree()

    def get_folder_name(self, folder_url):
        if not folder_url: return "Uncategorized"
        # Decode %20, remove trailing slash, take last part
        decoded = urllib.parse.unquote(folder_url).rstrip('/')
        name = os.path.basename(decoded)
        return name if name else "Uncategorized"

    def load_tree(self):
        self.file_tree.clear()
        files = self.db.get_all_files()
        
        # Organize: Category -> ParentDir -> Files
        structure = {}
        
        for path, filename, category, parent_dir, downloaded in files:
            if category not in structure:
                structure[category] = {}
            if parent_dir not in structure[category]:
                structure[category][parent_dir] = []
            structure[category][parent_dir].append((filename, path, downloaded))
            
        # Build Tree (Sorted)
        for category in sorted(structure.keys()):
            cat_item = QTreeWidgetItem(self.file_tree, [category, "Category"])
            cat_item.setExpanded(True)
            
            # Sort Folders by Name
            folders = structure[category]
            sorted_folders = sorted(folders.items(), key=lambda x: self.get_folder_name(x[0]).lower())
            
            for folder, file_list in sorted_folders:
                folder_name = self.get_folder_name(folder)
                folder_item = QTreeWidgetItem(cat_item, [folder_name, "Folder"])
                folder_item.setExpanded(False) # Collapse by default to keep clean
                
                # Sort Files
                sorted_files = sorted(file_list, key=lambda x: x[0].lower())
                
                for fname, fpath, downloaded in sorted_files:
                    name_display = f"[OFFLINE] {fname}" if downloaded else fname
                    file_item = QTreeWidgetItem(folder_item, [name_display, "File"])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, fpath)

    def filter_tree(self, text):
        query = text.lower()
        
        def traverse(item):
            has_search_match = False
            
            # Check children first (bottom-up to propagate match)
            for i in range(item.childCount()):
                child = item.child(i)
                child_has_match = traverse(child)
                has_search_match = has_search_match or child_has_match
            
            # Check self
            text_match = query in item.text(0).lower()
            should_show = has_search_match or text_match
            
            item.setHidden(not should_show)
            if should_show and query:
                item.setExpanded(True)
            elif not query:
                # Reset expansion if clear
                # Only expand top-level categories
                is_top = item.parent() is None
                item.setExpanded(is_top)
                
            return should_show

        # Prevent updates while filtering for performance
        self.file_tree.setUpdatesEnabled(False)
        for i in range(self.file_tree.topLevelItemCount()):
            traverse(self.file_tree.topLevelItem(i))
        self.file_tree.setUpdatesEnabled(True)

    def on_search_text_changed(self, text):
        self.debounce_timer.start()

    def perform_search(self, force_empty=False):
        query = "" if force_empty else self.search_bar.text()
        if len(query) > 0 and len(query) < 3:
            return 
        self.search_thread.search(query)

    def on_search_results(self, results):
        self.file_list.clear()
        if not results:
            item = QListWidgetItem("No results found")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
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
        if not url: return
        local_path = item.data(102)
        self.play_media(url, local_path)

    def on_tree_item_double_click(self, item, column):
        url = item.data(0, Qt.ItemDataRole.UserRole)
        if url:
             # Resolve local path if needed (simple check)
             local_path = self.db.get_local_path(url)
             self.play_media(url, local_path)

    def play_media(self, url, local_path):
        if local_path and os.path.exists(local_path):
            self.file_selected.emit(local_path)
        else:
            if local_path: # Path exists in DB but file missing
                QMessageBox.warning(self, "File Missing", "Local file not found. Streaming from server instead.")
            self.file_selected.emit(url)

    def open_context_menu(self, position):
        item = self.file_list.itemAt(position)
        if not item: return
        url = item.data(100)
        if not url: return
        
        menu = QMenu()
        download_action = menu.addAction("Download")
        download_action.triggered.connect(lambda: self.download_requested.emit(url, item.data(101)))
        menu.exec(self.file_list.mapToGlobal(position))
        
    def get_current_items(self):
        """Returns a list of (url, local_path) tuples from the current view."""
        items = []
        if self.tabs.currentIndex() == 0: # List View
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                # Skip "No results found" which has no URL
                if item.flags() & Qt.ItemFlag.ItemIsEnabled and item.data(100): 
                    items.append((item.data(100), item.data(102)))
        else: # Tree View
             iterator = QTreeWidgetItemIterator(self.file_tree)
             while iterator.value():
                 item = iterator.value()
                 url = item.data(0, Qt.ItemDataRole.UserRole)
                 if url:
                     local_path = self.db.get_local_path(url)
                     items.append((url, local_path))
                 iterator += 1
        return items

    def get_next_file(self, current_path):
        items = self.get_current_items()
        for i, (url, local_path) in enumerate(items):
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

