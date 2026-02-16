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
    next_requested = pyqtSignal()
    prev_requested = pyqtSignal()
    playlist_requested = pyqtSignal()
    
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
                                   osc=True)
                
                self.setup_bindings()

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

    def setup_bindings(self):
        @self.mpv.key_binding('SPACE')
        def toggle_pause(keydown=True):
            if keydown: self.pause()

        @self.mpv.key_binding('f')
        @self.mpv.key_binding('MOUSE_BTN0_DBL')
        def toggle_fullscreen(keydown=True):
            if keydown:
                if self.window().isFullScreen():
                    self.window().showNormal()
                else:
                    self.window().showFullScreen()

        @self.mpv.key_binding('ESC')
        def exit_fullscreen(keydown=True):
            if keydown and self.window().isFullScreen():
                self.window().showNormal()

        @self.mpv.key_binding('LEFT')
        def seek_small_back(keydown=True):
            if keydown: self.seek(-5)

        @self.mpv.key_binding('RIGHT')
        def seek_small_fwd(keydown=True):
            if keydown: self.seek(5)

        @self.mpv.key_binding('Shift+LEFT')
        def seek_med_back(keydown=True):
            if keydown: self.seek(-30)

        @self.mpv.key_binding('Shift+RIGHT')
        def seek_med_fwd(keydown=True):
            if keydown: self.seek(30)

        @self.mpv.key_binding('UP')
        def vol_up(keydown=True):
            if keydown: 
                try: self.mpv.volume += 5
                except: pass

        @self.mpv.key_binding('DOWN')
        def vol_down(keydown=True):
            if keydown:
                try: self.mpv.volume -= 5
                except: pass

        @self.mpv.key_binding('a')
        def cycle_audio(keydown=True):
            if keydown:
                try: self.mpv.cycle('aid')
                except: pass

        @self.mpv.key_binding('s')
        def cycle_sub(keydown=True):
            if keydown:
                try: self.mpv.cycle('sid')
                except: pass

        @self.mpv.key_binding('Alt+s')
        def toggle_sub(keydown=True):
            if keydown:
                try: self.mpv.cycle('sub-visibility')
                except: pass

        @self.mpv.key_binding('PGUP')
        def prev_chapter(keydown=True):
            if keydown:
                try: self.mpv.chapter += -1
                except: pass

        @self.mpv.key_binding('PGDWN')
        def next_chapter(keydown=True):
            if keydown:
                try: self.mpv.chapter += 1
                except: pass

        @self.mpv.key_binding('n')
        def next_file(keydown=True):
            if keydown: self.next_requested.emit()

        @self.mpv.key_binding('N') # Shift+n usually sends 'N'
        def prev_file(keydown=True):
            if keydown: self.prev_requested.emit()

        @self.mpv.key_binding('p')
        def show_playlist(keydown=True):
            if keydown: self.playlist_requested.emit()

    def show_error_placeholder(self):
        msg = QLabel("MPV Library not found.\nPlease install 'mpv' and 'libmpv-dev'.\nOn Ubuntu: sudo apt install mpv libmpv-dev")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: red; font-size: 16px;")
        self.layout().replaceWidget(self.container, msg)
        self.container.deleteLater()
        self.container = None
    
    # mouseDoubleClickEvent and keyPressEvent removed in favor of MPV bindings

    def play(self, url):
        if self.mpv:
            self.mpv.play(url)

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
