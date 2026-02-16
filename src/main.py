import traceback
import datetime
import locale
import sys

# Fix for MPV on Linux (Segmentation Fault)
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except Exception as e:
    print(f"Warning: Could not set locale: {e}")

from PyQt6.QtWidgets import QMessageBox, QApplication
from src.ui.mainwindow import MainWindow

def exception_hook(exctype, value, tb):
    """Global exception handler to log crashes."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("Uncaught exception:", error_msg)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"[{timestamp}] CRASH REPORT:\n{error_msg}\n{'-'*60}\n"
    
    try:
        with open("crash.log", "a") as f:
            f.write(log_content)
    except Exception as e:
        print(f"Failed to write crash log: {e}")
        
    # Show error dialog if app is running
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Application Crashed")
        msg.setInformativeText("An unexpected error occurred. A crash log has been saved to 'crash.log'.")
        msg.setDetailedText(error_msg)
        msg.exec()
        
    sys.exit(1)

def main():
    # Fix for MPV on Linux (Segmentation Fault)
    try:
        locale.setlocale(locale.LC_NUMERIC, 'C')
    except Exception as e:
        print(f"Warning: Could not set locale: {e}")

    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    app.setApplicationName("DhakaFlix Streamer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
