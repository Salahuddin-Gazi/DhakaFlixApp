import aiohttp
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from PyQt6.QtCore import QObject, pyqtSignal
import time

class HttpClient(QObject):
    # Signals
    progress_signal = pyqtSignal(str) 
    file_found_signal = pyqtSignal(dict) 
    finished_signal = pyqtSignal()
    
    def __init__(self, base_url="http://172.16.50.9/DHAKA-FLIX-9/"):
        super().__init__()
        self.base_url = base_url
        self.stop_requested = False
        self.semaphore = asyncio.Semaphore(20) # Limit concurrent requests

    def scan_server(self):
        self.stop_requested = False
        self.tasks = []
        self.progress_signal.emit(f"Starting async scan of {self.base_url}...")
        
        try:
            asyncio.run(self._run_crawl())
        except asyncio.CancelledError:
             self.progress_signal.emit("Scan cancelled.")
        except Exception as e:
            self.progress_signal.emit(f"Error: {e}")
        
        self.progress_signal.emit("Scan complete.")
        self.finished_signal.emit()

    async def _run_crawl(self):
        async with aiohttp.ClientSession() as session:
            await self._crawl_recursive(session, self.base_url)

    async def _crawl_recursive(self, session, url, depth=0, max_depth=10):
        if self.stop_requested or depth > max_depth:
            return

        html_text = ""
        # print(f"Crawling {url}") # Debug
        async with self.semaphore:
            if self.stop_requested: return
            try:
                # Use a smaller timeout for testing/speed
                async with session.get(url, timeout=5) as response:
                    if response.status != 200:
                        print(f"Status {response.status} for {url}")
                        return
                    if self.stop_requested: return
                    html_text = await response.text()
                    # print(f"Fetched {len(html_text)} bytes from {url}") # Debug
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                return

        soup = BeautifulSoup(html_text, 'html.parser')
        links = soup.find_all('a')
        # print(f"Found {len(links)} links in {url}") # Debug
        
        # Collect tasks for this level
        sub_tasks = []

        for link in soup.find_all('a'):
            if self.stop_requested:
                break

            href = link.get('href')
            name = link.text.strip()
            
            if name in ['Parent Directory', '../', './'] or href in ['../', './'] or not href:
                continue
            
            if '?' in href:
                continue

            # Handle relative URLs correctly
            full_url = urllib.parse.urljoin(url, href)
            
            if href.endswith('/'):
                # Directory: Queue it
                task = asyncio.create_task(self._crawl_recursive(session, full_url, depth + 1, max_depth))
                sub_tasks.append(task)
                self.tasks.append(task)
            else:
                # File
                if any(name.lower().endswith(ext) for ext in ['.mkv', '.mp4', '.avi', '.mp3', '.flac']):
                    self.file_found_signal.emit({
                        "path": full_url,
                        "filename": name,
                        "parent_dir": url
                    })
        
        if sub_tasks:
            # Wait for subtasks, but return early if stopped
            done, pending = await asyncio.wait(sub_tasks, return_when=asyncio.FIRST_EXCEPTION)
            # Creating tasks in recursive loop without gathering them at top level can be tricky
            # But here we await them at each level, which effectively makes it depth-first-ish parallel
            pass

    def stop(self):
        self.stop_requested = True
        # Cancel all running tasks
        for task in getattr(self, 'tasks', []):
            task.cancel()
