from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                             QProgressBar, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

class DownloadItemWidget(QWidget):
    def __init__(self, filename):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.label = QLabel(filename)
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        
    def update_progress(self, percent):
        self.progress.setValue(int(percent))
        if percent >= 100:
            self.label.setText(f"{self.label.text()} (Completed)")

class DownloadsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.active_items = {} # url -> (item, widget)

    def add_download(self, url, filename):
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(item.sizeHint()) # Adjust later if needed
        
        widget = DownloadItemWidget(filename)
        item.setSizeHint(widget.sizeHint())
        
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        
        self.active_items[url] = (item, widget)

    def update_progress(self, url, percent):
        if url in self.active_items:
            _, widget = self.active_items[url]
            widget.update_progress(percent)

    def mark_completed(self, url):
        if url in self.active_items:
            _, widget = self.active_items[url]
            widget.update_progress(100)
            # Could remove or move to completed section
            # del self.active_items[url] 
