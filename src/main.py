import sys
from PyQt6.QtWidgets import QApplication
from src.ui.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DhakaFlix Streamer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
