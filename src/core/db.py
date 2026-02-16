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
        self.cursor = self.conn.cursor()

    def init_db(self):
        self.cursor.execute('''
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

    def clear_index(self):
        self.cursor.execute('DELETE FROM files')
        self.conn.commit()

    def add_file(self, path, filename, parent_dir):
        try:
            # Simple category detection based on parent dir or extension
            category = "Other"
            if "Anime" in path or "Anime" in parent_dir:
                category = "Anime"
            elif "Movies" in path or "Movies" in parent_dir:
                category = "Movies"
            elif "Series" in path or "Series" in parent_dir:
                category = "Series"
                
            self.cursor.execute('''
                INSERT OR IGNORE INTO files (path, filename, category, parent_dir)
                VALUES (?, ?, ?, ?)
            ''', (path, filename, category, parent_dir))
        except sqlite3.Error as e:
            print(f"Error adding file {filename}: {e}")

    def commit(self):
        self.conn.commit()

    def search(self, query):
        if not query:
            self.cursor.execute('''
                SELECT path, filename, category, local_path, downloaded FROM files 
                ORDER BY id DESC LIMIT 100
            ''')
        else:
            self.cursor.execute('''
                SELECT path, filename, category, local_path, downloaded FROM files 
                WHERE filename LIKE ? OR parent_dir LIKE ?
                LIMIT 100
            ''', (f'%{query}%', f'%{query}%'))
        return self.cursor.fetchall()

    def get_all_files(self):
        self.cursor.execute('SELECT path, filename, category, parent_dir, downloaded FROM files')
        return self.cursor.fetchall()

    def mark_downloaded(self, url, local_path):
        self.cursor.execute('''
            UPDATE files SET local_path = ?, downloaded = 1 WHERE path = ?
        ''', (local_path, url))
        self.conn.commit()
    
    def get_local_path(self, url):
        self.cursor.execute('SELECT local_path FROM files WHERE path = ? AND downloaded = 1', (url,))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def get_all_categories(self):
        self.cursor.execute('SELECT DISTINCT category FROM files')
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()
