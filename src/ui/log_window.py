from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt

class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Indexing Log")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel("Real-time indexing log:")
        layout.addWidget(self.info_label)
        
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Consolas, Monospace; font-size: 10pt;")
        layout.addWidget(self.log_area)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.hide) # Just hide, don't destroy
        layout.addWidget(self.btn_close)
        
    def append_log(self, text):
        self.log_area.appendPlainText(text)
        
    def clear_log(self):
        self.log_area.clear()
