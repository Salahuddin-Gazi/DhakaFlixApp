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
        def toggle_pause(state=None, *args):
            if state and state[0] in ('d', 'p'): self.pause()

        @self.mpv.key_binding('f')
        @self.mpv.key_binding('MOUSE_BTN0_DBL')
        def toggle_fullscreen(state=None, *args):
            if state and state[0] in ('d', 'p'):
                if self.window().isFullScreen():
                    self.window().showNormal()
                else:
                    self.window().showFullScreen()

        @self.mpv.key_binding('ESC')
        def exit_fullscreen(state=None, *args):
            if state and state[0] in ('d', 'p') and self.window().isFullScreen():
                self.window().showNormal()

        @self.mpv.key_binding('LEFT')
        def seek_small_back(state=None, *args):
            if state and state[0] in ('d', 'p'): self.seek(-5)

        @self.mpv.key_binding('RIGHT')
        def seek_small_fwd(state=None, *args):
            if state and state[0] in ('d', 'p'): self.seek(5)

        @self.mpv.key_binding('Shift+LEFT')
        def seek_med_back(state=None, *args):
            if state and state[0] in ('d', 'p'): self.seek(-30)

        @self.mpv.key_binding('Shift+RIGHT')
        def seek_med_fwd(state=None, *args):
            if state and state[0] in ('d', 'p'): self.seek(30)

        @self.mpv.key_binding('UP')
        def vol_up(state=None, *args):
            if state and state[0] in ('d', 'p'): 
                try: self.mpv.volume += 5
                except: pass

        @self.mpv.key_binding('DOWN')
        def vol_down(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.volume -= 5
                except: pass

        @self.mpv.key_binding('a')
        def cycle_audio(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.cycle('aid')
                except: pass

        @self.mpv.key_binding('s')
        def cycle_sub(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.cycle('sid')
                except: pass

        @self.mpv.key_binding('Alt+s')
        def toggle_sub(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.cycle('sub-visibility')
                except: pass

        @self.mpv.key_binding('PGUP')
        def prev_chapter(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.chapter += -1
                except: pass

        @self.mpv.key_binding('PGDWN')
        def next_chapter(state=None, *args):
            if state and state[0] in ('d', 'p'):
                try: self.mpv.chapter += 1
                except: pass

        @self.mpv.key_binding('n')
        def next_file(state=None, *args):
            if state and state[0] in ('d', 'p'): 
                self.next_requested.emit()

        @self.mpv.key_binding('N') # Shift+n usually sends 'N'
        def prev_file(state=None, *args):
            if state and state[0] in ('d', 'p'): 
                self.prev_requested.emit()

        @self.mpv.key_binding('p')
        def show_playlist(state=None, *args):
            if state and state[0] in ('d', 'p'): self.playlist_requested.emit()

        # Observers for OSD
        @self.mpv.property_observer('aid')
        def on_aid_change(name, value):
            self.show_track_osd("Audio", "audio", value)

        @self.mpv.property_observer('sid')
        def on_sid_change(name, value):
            self.show_track_osd("Sub", "sub", value)

        @self.mpv.property_observer('media-title')
        def on_title_change(name, value):
            if value:
                self.show_osd(f"Playing: {value}", 3000)

        @self.mpv.property_observer('chapter')
        def on_chapter_change(name, value):
            if value is not None:
                # Try to get chapter title
                title = ""
                try:
                    chapters = self.mpv.chapter_list
                    if chapters and 0 <= value < len(chapters):
                        title = chapters[value].get('title', '')
                except: pass
                
                msg = f"Chapter: {value+1}"
                if title: msg += f" - {title}"
                self.show_osd(msg)

    def show_track_osd(self, label, type_name, track_id):
        if track_id is None or track_id is False:
            self.show_osd(f"{label}: Off")
            return
        
        try:
            # We must be careful accessing mpv properties from callback thread
            # but track_list should be safe enough usually
            tracks = self.mpv.track_list
            for t in tracks:
                if t['type'] == type_name and t['id'] == track_id:
                    lang = t.get('lang', 'unk').upper()
                    title = t.get('title', '')
                    msg = f"{label}: {lang}"
                    if title: msg += f" - {title}"
                    self.show_osd(msg)
                    return
        except Exception as e:
            print(f"OSD Error: {e}")
        
        self.show_osd(f"{label}: {track_id}")

    def show_osd(self, text, duration=2000):
        try:
            self.mpv.command('show-text', text, duration)
        except: pass

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
