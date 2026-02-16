import http.server
import socketserver
import os
import sys

PORT = 8001
DIRECTORY = "tests/mock_data"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    # Create some dummy files if they don't exist
    os.makedirs(f"{DIRECTORY}/DHAKA-FLIX-9/Anime/One Piece", exist_ok=True)
    with open(f"{DIRECTORY}/DHAKA-FLIX-9/Anime/One Piece/episode1.mkv", "w") as f:
        f.write("dummy video content")
    with open(f"{DIRECTORY}/DHAKA-FLIX-9/video.mp4", "w") as f:
        f.write("dummy video content")
    
    # Ultimate Test File
    os.makedirs(f"{DIRECTORY}/DHAKA-FLIX-9/Movies", exist_ok=True)
    with open(f"{DIRECTORY}/DHAKA-FLIX-9/Movies/2001_A_Space_Odyssey.mkv", "w") as f:
        f.write("I'm sorry Dave, I'm afraid I can't do that. (Dummy Video Content)")

    print(f"Serving {DIRECTORY} at port {PORT}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
