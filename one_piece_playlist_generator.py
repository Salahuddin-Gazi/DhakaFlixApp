import urllib.request
import urllib.parse
import re
import sys
from html.parser import HTMLParser

# Base configuration
BASE_URL = "http://172.16.50.9/DHAKA-FLIX-9/Anime%20%26%20Cartoon%20TV%20Series/Anime-TV%20Series%20%E2%99%A6%20%20N%20%20%E2%80%94%20%20S/One%20Piece%20%28TV%20Cartoon%201999%E2%80%93%20%29%201080p%20%5BDual%20Audio%5D/"
START_SEASON = 16
OUTPUT_FILE = "One_Piece_Seasons_16_to_Latest.m3u"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])

def get_links(url):
    try:
        # Properly quote the URL to handle spaces and special chars if they aren't already
        # However, the provided URL seems to be already encoded. We try to use it as is first.
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            
        parser = LinkParser()
        parser.feed(html_content)
        return parser.links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def is_video_file(filename):
    video_extensions = ('.mkv', '.mp4', '.avi', '.m4v')
    return filename.lower().endswith(video_extensions)

def extract_season_number(folder_name):
    # Matches "Season 16", "Season 17", etc.
    match = re.search(r'Season\s+(\d+)', folder_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def main():
    print(f"Scanning for seasons starting from Season {START_SEASON}...")
    print(f"Base URL: {BASE_URL}")

    # 1. Get main directory listing
    main_links = get_links(BASE_URL)
    
    season_folders = []
    for link in main_links:
        # Decode the link to check the folder name
        decoded_name = urllib.parse.unquote(link)
        season_num = extract_season_number(decoded_name)
        
        if season_num is not None and season_num >= START_SEASON:
            full_url = urllib.parse.urljoin(BASE_URL, link)
            season_folders.append((season_num, decoded_name, full_url))
    
    # Sort seasons numerically
    season_folders.sort(key=lambda x: x[0])
    
    if not season_folders:
        print("No matching seasons found via scanning. Please check the URL or network connection.")
        # Sometimes directory listings have absolute paths or different structures.
        return

    print(f"Found {len(season_folders)} seasons to process: {[s[0] for s in season_folders]}")

    all_video_urls = []

    # 2. Process each season folder
    for season_num, season_name, season_url in season_folders:
        print(f"Crawling {season_name}...")
        file_links = get_links(season_url)
        
        videos_in_season = []
        for file_link in file_links:
            decoded_filename = urllib.parse.unquote(file_link)
            if is_video_file(decoded_filename):
                # Construct the full absolute URL for the video file
                video_url = urllib.parse.urljoin(season_url, file_link)
                videos_in_season.append(video_url)
        
        # Sort videos alphabetically (usually keeps episodes in order)
        videos_in_season.sort()
        all_video_urls.extend(videos_in_season)
        print(f"  -> Found {len(videos_in_season)} episodes.")

    # 3. Write to M3U file
    if all_video_urls:
        print(f"\nGeneratring playlist with {len(all_video_urls)} total episodes...")
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for url in all_video_urls:
                    # VLC playlists work best with encoded URLs
                    f.write(f"{url}\n")
            
            print(f"Success! Playlist saved to: {OUTPUT_FILE}")
            print("You can now open this file with VLC Media Player.")
        except IOError as e:
            print(f"Error writing file: {e}")
    else:
        print("No video files found in the scanned directories.")

if __name__ == "__main__":
    main()
