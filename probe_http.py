import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

BASE_URL = "http://172.16.50.9/DHAKA-FLIX-9/"

def get_structure(url, depth=0, max_depth=2):
    if depth > max_depth:
        return {"type": "dir", "children": {}}
    
    structure = {}
    try:
        print(f"Crawling: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Apache/Nginx directory listings usually have links
        for link in soup.find_all('a'):
            href = link.get('href')
            name = link.text.strip()
            
            # Skip parent directory links
            if name in ['Parent Directory', '../', './'] or href in ['../', './']:
                continue
            
            # Skip distinct query params or weird sorting links usually found in headers
            if '?' in href:
                continue

            # Check if it looks like a file or directory
            # Directory names in these listings usually end with /
            is_dir = href.endswith('/')
            
            # Construct full URL
            full_url = urllib.parse.urljoin(url, href)
            
            if is_dir:
                structure[name] = get_structure(full_url, depth + 1, max_depth)
            else:
                structure[name] = "file"
                
    except Exception as e:
        return {"error": str(e)}
        
    return structure

def main():
    print(f"Attempting to crawl {BASE_URL}...")
    try:
        structure = get_structure(BASE_URL)
        
        print("\n--- HTTP STRUCTURE START ---")
        print(json.dumps(structure, indent=2))
        print("--- HTTP STRUCTURE END ---")
        
    except Exception as e:
        print(f"Crawl failed: {e}")

if __name__ == "__main__":
    main()
