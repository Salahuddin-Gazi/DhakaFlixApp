import ftplib
import json
import sys

FTP_HOST = "172.16.50.9"
TIMEOUT = 5

def get_structure(ftp, path, depth=0, max_depth=2):
    if depth > max_depth:
        return {"type": "dir", "children": {}}
    
    structure = {}
    try:
        ftp.cwd(path)
        items = []
        ftp.retrlines('LIST', items.append)
        
        for item in items:
            parts = item.split(maxsplit=8)
            if len(parts) < 9:
                continue
            
            permissions = parts[0]
            name = parts[8]
            
            if name in ['.', '..']:
                continue
                
            if permissions.startswith('d'):
                structure[name] = get_structure(ftp, f"{path}/{name}", depth + 1, max_depth)
                ftp.cwd(path) # Go back up
            else:
                structure[name] = "file"
                
    except Exception as e:
        return {"error": str(e)}
        
    return structure

def main():
    print(f"Attempting to connect to {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST, timeout=TIMEOUT)
        ftp.login() # Anonymous login
        print("Connected successfully.")
        
        print("Scanning directory structure (depth=2)...")
        structure = get_structure(ftp, "/")
        
        print("\n--- FTP STRUCTURE START ---")
        print(json.dumps(structure, indent=2))
        print("--- FTP STRUCTURE END ---")
        
        ftp.quit()
    except Exception as e:
        print(f"Connection failed: {e}")
        # Try a simple connect check without traversal if full logic fails
        print("Please manually confirm if this IP is reachable and if it requires a password.")

if __name__ == "__main__":
    main()
