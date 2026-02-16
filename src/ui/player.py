import locale
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

# Set locale for MPV compatibility
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except locale.Error:
    print("Locale setting failed")

try:
    import mpv
    MPV_AVAILABLE = True
except (ImportError, OSError):
    MPV_AVAILABLE = False
    print("MPV not available")

class PlayerWidget(QWidget):
    # Signals
    position_changed = pyqtSignal(float)
    duration_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Container for MPV
        self.container = QFrame(self)
        self.layout().addWidget(self.container)
        
        self.mpv = None
        
        if MPV_AVAILABLE:
            try:
                # Initialize MPV
                self.mpv = mpv.MPV(wid=str(int(self.container.winId())), 
                                   input_default_bindings=True, 
                                   input_vo_keyboard=True,
                                   osc=True) # Enable On-Screen Controller
                
                # MPV Property observers
                @self.mpv.property_observer('time-pos')
                def time_observer(_name, value):
                    if value is not None:
                        self.position_changed.emit(value)

                @self.mpv.property_observer('duration')
                def duration_observer(_name, value):
                    if value is not None:
                        self.duration_changed.emit(value)
            except Exception as e:
                print(f"Failed to initialize MPV: {e}")
                self.show_error_placeholder()
        else:
            self.show_error_placeholder()

    def show_error_placeholder(self):
        msg = QLabel("MPV Library not found.\nPlease install 'mpv' and 'libmpv-dev'.\nOn Ubuntu: sudo apt install mpv libmpv-dev")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: red; font-size: 16px;")
        self.layout().replaceWidget(self.container, msg)
        self.container.deleteLater()
        self.container = None

    def mouseDoubleClickEvent(self, event):
        if self.window().isFullScreen():
            self.window().showNormal()
        else:
            self.window().showFullScreen()

    def keyPressEvent(self, event):
        if not self.mpv:
            return
            
        key = event.key()
        
        if key == Qt.Key.Key_Space:
            self.pause()
        elif key == Qt.Key.Key_F:
            if self.window().isFullScreen():
                self.window().showNormal()
            else:
                self.window().showFullScreen()
        elif key == Qt.Key.Key_Escape:
            if self.window().isFullScreen():
                self.window().showNormal()
        elif key == Qt.Key.Key_Left:
            self.seek(-5)
        elif key == Qt.Key.Key_Right:
            self.seek(5)
        elif key == Qt.Key.Key_Up:
            try:
                self.mpv.volume += 5
            except: pass
        elif key == Qt.Key.Key_Down:
            try:
                self.mpv.volume -= 5
            except: pass
        else:
            super().keyPressEvent(event)

    def play(self, url):
        if self.mpv:
            self.mpv.play(url)
            self.setFocus() # Grab focus for shortcuts

    def stop(self):
        if self.mpv:
            self.mpv.stop()

    def pause(self):
        if self.mpv:
            self.mpv.pause = not self.mpv.pause

    def seek(self, seconds):
        if self.mpv:
            self.mpv.seek(seconds)

    def terminate(self):
        if self.mpv:
            self.mpv.terminate()
