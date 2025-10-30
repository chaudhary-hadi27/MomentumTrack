import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.db_path = 'data/momentumtrack.db'
        os.makedirs('data', exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        ''')

        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                target_date TEXT,
                progress INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Time blocks table (8/8/8 tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                work_hours REAL DEFAULT 0,
                personal_hours REAL DEFAULT 0,
                sleep_hours REAL DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    # Task CRUD operations
    def add_task(self, title, description='', category='work', priority='medium', due_date=None):
        """Add a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, category, priority, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, category, priority, due_date))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id

    def get_all_tasks(self, status=None):
        """Get all tasks, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def update_task_status(self, task_id, status):
        """Update task status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        cursor.execute('''
            UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?
        ''', (status, completed_at, task_id))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        """Delete a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    # Goal CRUD operations
    def add_goal(self, title, description='', target_date=None):
        """Add a new goal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (title, description, target_date)
            VALUES (?, ?, ?)
        ''', (title, description, target_date))
        conn.commit()
        goal_id = cursor.lastrowid
        conn.close()
        return goal_id

    def get_all_goals(self):
        """Get all goals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM goals ORDER BY created_at DESC')
        goals = cursor.fetchall()
        conn.close()
        return goals

    def update_goal_progress(self, goal_id, progress):
        """Update goal progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE goals SET progress = ? WHERE id = ?', (progress, goal_id))
        conn.commit()
        conn.close()

    # Time tracking
    def update_time_block(self, date, work=0, personal=0, sleep=0):
        """Update time block for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO time_blocks (date, work_hours, personal_hours, sleep_hours)
            VALUES (?, ?, ?, ?)
        ''', (date, work, personal, sleep))
        conn.commit()
        conn.close()

    def get_time_block(self, date):
        """Get time block for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM time_blocks WHERE date = ?', (date,))
        result = cursor.fetchone()
        conn.close()
        return result

    # Analytics
    def get_completion_rate(self):
        """Calculate task completion rate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM tasks')
        total = cursor.fetchone()[0]
        conn.close()
        return (completed / total * 100) if total > 0 else 0