import sqlite3
import tkinter as tk
from tkinter import ttk

class LibraryDatabase:
    def __init__(self, app, db_name="library.db"):
        self.app = app
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Students table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                rfid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                section TEXT
            )
        """)

        # Logs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                timein TEXT,
                timeout TEXT,
                purpose TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purposes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()


        self.conn.commit()

    def add_student(self, rfid, name, grade, section):
        self.cursor.execute("INSERT OR REPLACE INTO students (rfid, name, grade, section) VALUES (?, ?, ?, ?)",
                            (rfid, name, grade, section))
        self.conn.commit()

    def get_student_by_rfid(self, rfid):
        self.cursor.execute("SELECT * FROM students WHERE rfid=?", (rfid,))
        return self.cursor.fetchone()

    def add_log(self, name, timein, timeout, purpose):
        self.cursor.execute("INSERT INTO logs (name, timein, timeout, purpose) VALUES (?, ?, ?, ?)",
                            (name, timein, timeout, purpose))
        self.conn.commit()

    def get_logs(self):
        self.cursor.execute("SELECT * FROM logs")
        return self.cursor.fetchall()
    
    def get_student_by_rfid(self, rfid):
        conn = sqlite3.connect("library.db")
        cur = conn.cursor()
        cur.execute("SELECT rfid, name, grade, section FROM students WHERE rfid = ?", (rfid,))
        student = cur.fetchone()
        conn.close()
        return student
    
    def update_timeout(self, log_id, timeout):
        self.cursor.execute("UPDATE logs SET timeout=? WHERE id=?", (timeout, log_id))
        self.conn.commit()
    
    def get_purposes(self):
            self.cursor.execute("SELECT name FROM purposes ORDER BY name")
            return [row[0] for row in self.cursor.fetchall()]

    def add_purpose(self, name):
            try:
                self.cursor.execute("INSERT INTO purposes (name) VALUES (?)", (name,))
                self.conn.commit()
                return True
            except:
                return False

    def delete_purpose(self, name):
            self.cursor.execute("DELETE FROM purposes WHERE name = ?", (name,))
            self.conn.commit()
