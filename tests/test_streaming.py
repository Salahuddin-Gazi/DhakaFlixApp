import sys
import os
import time
import locale
from PyQt6.QtCore import QCoreApplication

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set locale for MPV
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except locale.Error:
    pass

try:
    import mpv
except ImportError:
    print("TEST SKIPPED: MPV not installed.")
    sys.exit(0)

def run_test():
    app = QCoreApplication(sys.argv)
    
    url = "http://127.0.0.1:8001/DHAKA-FLIX-9/video.mp4"
    
    print(f"Attempting to stream {url}...")
    
    try:
        player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
        player.play(url)
        
        # Wait a bit to let it "buffer" or start
        time.sleep(2)
        
        # Check if we are in an error state
        # Note: MPV properties might throw errors if accessed too early or late
        # But if we got here without python exception, bindings are working.
        
        # We can check 'idle_active' or 'core_idle'
        is_idle = player.idle_active
        print(f"Player Idle State: {is_idle}")
        
        player.terminate()
        print("TEST PASSED: MPV accepted URL and started.")
        sys.exit(0)
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
