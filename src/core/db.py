import sqlite3
import os

class DatabaseHandler:
    def __init__(self, db_path="index.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_db()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # self.cursor removed to prevent thread safety issues

    def init_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    filename TEXT,
                    category TEXT,
                    parent_dir TEXT,
                    local_path TEXT,
                    downloaded BOOLEAN DEFAULT 0
                )
            ''')
            self.conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print(f"DB Init Error: {e}")

    def clear_index(self):
        with self.conn:
            self.conn.execute('DELETE FROM files')

    def add_file(self, path, filename, parent_dir):
        try:
            # Simple category detection
            category = "Other"
            if "Anime" in path or "Anime" in parent_dir:
                category = "Anime"
            elif "Movies" in path or "Movies" in parent_dir:
                category = "Movies"
            elif "Series" in path or "Series" in parent_dir:
                category = "Series"
                
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO files (path, filename, category, parent_dir)
                VALUES (?, ?, ?, ?)
            ''', (path, filename, category, parent_dir))
            cursor.close()
        except sqlite3.Error as e:
            print(f"Error adding file {filename}: {e}")

    def commit(self):
        try:
            self.conn.commit()
        except: pass

    def search(self, query):
        cursor = self.conn.cursor()
        if not query:
            cursor.execute('''
                SELECT path, filename, category, local_path, downloaded FROM files 
                ORDER BY id DESC LIMIT 100
            ''')
        else:
            cursor.execute('''
                SELECT path, filename, category, local_path, downloaded FROM files 
                WHERE filename LIKE ? OR parent_dir LIKE ?
                LIMIT 100
            ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_all_files(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT path, filename, category, parent_dir, downloaded FROM files')
        results = cursor.fetchall()
        cursor.close()
        return results

    def mark_downloaded(self, url, local_path):
        with self.conn:
            self.conn.execute('''
                UPDATE files SET local_path = ?, downloaded = 1 WHERE path = ?
            ''', (local_path, url))
    
    def get_local_path(self, url):
        cursor = self.conn.cursor()
        cursor.execute('SELECT local_path FROM files WHERE path = ? AND downloaded = 1', (url,))
        res = cursor.fetchone()
        cursor.close()
        return res[0] if res else None

    def get_all_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM files')
        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return results

    def close(self):
        if self.conn:
            self.conn.close()
