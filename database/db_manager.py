"""
Enhanced Database Manager with Advanced Task Scheduling
Supports start/end times, reminders, motivational quotes, and live progress
"""

import sqlite3
import os
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        self.db_path = 'data/momentumtrack.db'
        os.makedirs('data', exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        """Create tables with enhanced schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Enhanced Tasks table with scheduling
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'work',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                
                -- Scheduling fields
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_type TEXT DEFAULT 'today',
                custom_end_date TEXT,
                
                -- Motivation & Reminders
                motivational_quote TEXT,
                reminder_enabled INTEGER DEFAULT 1,
                reminder_interval INTEGER DEFAULT 30,
                
                -- Timestamps
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                
                -- Progress tracking
                last_viewed_at TEXT,
                time_spent_minutes INTEGER DEFAULT 0
            )
        ''')

        # Task reminders history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                reminder_time TEXT,
                sent INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')

        # Task progress logs (for live tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                action TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
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
                date TEXT NOT NULL UNIQUE,
                work_hours REAL DEFAULT 0,
                personal_hours REAL DEFAULT 0,
                sleep_hours REAL DEFAULT 0
            )
        ''')

        # Daily statistics (for live progress)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                tasks_created INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                completion_rate REAL DEFAULT 0,
                total_time_spent INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    # ==================== ENHANCED TASK CRUD ====================

    def add_task(self, title, description='', category='work', priority='medium',
                 start_time=None, end_time=None, duration_type='today',
                 custom_end_date=None, motivational_quote='',
                 reminder_enabled=True, reminder_interval=30):
        """
        Add a new task with scheduling

        Args:
            title: Task title (required)
            start_time: Start time in format "HH:MM" (required)
            end_time: End time in format "HH:MM" (optional)
            duration_type: 'today', 'week', 'month', 'year', 'custom'
            custom_end_date: If duration_type='custom', date in "YYYY-MM-DD"
            motivational_quote: Inspirational quote for the task
            reminder_enabled: Enable reminders
            reminder_interval: Minutes between reminders (default 30)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Validate start_time is provided
        if not start_time:
            raise ValueError("Start time is required!")

        try:
            cursor.execute('''
                INSERT INTO tasks (
                    title, description, category, priority,
                    start_time, end_time, duration_type, custom_end_date,
                    motivational_quote, reminder_enabled, reminder_interval
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, category, priority,
                  start_time, end_time, duration_type, custom_end_date,
                  motivational_quote, 1 if reminder_enabled else 0, reminder_interval))

            conn.commit()
            task_id = cursor.lastrowid

            # Create reminders if enabled
            if reminder_enabled and end_time:
                self._create_reminders(task_id, start_time, end_time, reminder_interval)

            # Log task creation
            self._log_task_progress(task_id, 'created', 'Task created')

            # Update daily stats
            self._update_daily_stats('created')

            return task_id

        finally:
            conn.close()

    def _create_reminders(self, task_id, start_time, end_time, interval_minutes):
        """Create reminder entries between start and end time"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Parse times
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))

            start_datetime = datetime.now().replace(hour=start_hour, minute=start_min, second=0)
            end_datetime = datetime.now().replace(hour=end_hour, minute=end_min, second=0)

            # If end time is before start time, it's next day
            if end_datetime <= start_datetime:
                end_datetime += timedelta(days=1)

            # Create reminders at intervals
            current_time = start_datetime
            while current_time < end_datetime:
                cursor.execute('''
                    INSERT INTO task_reminders (task_id, reminder_time)
                    VALUES (?, ?)
                ''', (task_id, current_time.strftime('%Y-%m-%d %H:%M:%S')))
                current_time += timedelta(minutes=interval_minutes)

            conn.commit()
        finally:
            conn.close()

    def get_all_tasks(self, status=None, duration_filter=None):
        """
        Get tasks with optional filters

        Args:
            status: 'pending', 'completed', 'all', or None
            duration_filter: 'today', 'week', 'month', 'year', or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if status and status != 'all':
            query += ' AND status = ?'
            params.append(status)

        # Filter by duration if specified
        if duration_filter:
            today = datetime.now().date()

            if duration_filter == 'today':
                query += ' AND DATE(created_at) = ?'
                params.append(today.isoformat())
            elif duration_filter == 'week':
                week_start = today - timedelta(days=today.weekday())
                query += ' AND DATE(created_at) >= ?'
                params.append(week_start.isoformat())
            elif duration_filter == 'month':
                month_start = today.replace(day=1)
                query += ' AND DATE(created_at) >= ?'
                params.append(month_start.isoformat())
            elif duration_filter == 'year':
                year_start = today.replace(month=1, day=1)
                query += ' AND DATE(created_at) >= ?'
                params.append(year_start.isoformat())

        query += ' ORDER BY start_time ASC, created_at DESC'

        cursor.execute(query, params)
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def get_tasks_by_duration_type(self, duration_type):
        """Get tasks filtered by their duration_type field"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE duration_type = ? 
            ORDER BY start_time ASC
        ''', (duration_type,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def get_active_tasks_for_time(self, current_time=None):
        """Get tasks that should be active at the given time"""
        if not current_time:
            current_time = datetime.now().time()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = 'pending'
            AND time(start_time) <= time(?)
            AND (end_time IS NULL OR time(end_time) >= time(?))
            ORDER BY start_time ASC
        ''', (current_time.strftime('%H:%M'), current_time.strftime('%H:%M')))
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def update_task_status(self, task_id, status):
        """Update task status and track progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        completed_at = datetime.now().isoformat() if status == 'completed' else None

        cursor.execute('''
            UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?
        ''', (status, completed_at, task_id))

        conn.commit()
        conn.close()

        # Log progress
        self._log_task_progress(task_id, 'status_changed', f'Status changed to {status}')

        # Update daily stats
        if status == 'completed':
            self._update_daily_stats('completed')

    def update_task_time_spent(self, task_id, minutes):
        """Update time spent on a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET time_spent_minutes = time_spent_minutes + ?,
                last_viewed_at = ?
            WHERE id = ?
        ''', (minutes, datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        """Delete a task and its related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        cursor.execute('DELETE FROM task_reminders WHERE task_id = ?', (task_id,))
        cursor.execute('DELETE FROM task_progress WHERE task_id = ?', (task_id,))
        conn.commit()
        conn.close()

    # ==================== PROGRESS TRACKING ====================

    def _log_task_progress(self, task_id, action, notes=''):
        """Log task progress for analytics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO task_progress (task_id, action, notes)
            VALUES (?, ?, ?)
        ''', (task_id, action, notes))
        conn.commit()
        conn.close()

    def _update_daily_stats(self, action):
        """Update daily statistics (LIVE data, no dummy)"""
        today = datetime.now().date().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get or create today's stats
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (today,))
        stats = cursor.fetchone()

        if not stats:
            cursor.execute('''
                INSERT INTO daily_stats (date, tasks_created, tasks_completed)
                VALUES (?, 0, 0)
            ''', (today,))
            conn.commit()

        # Update based on action
        if action == 'created':
            cursor.execute('''
                UPDATE daily_stats 
                SET tasks_created = tasks_created + 1
                WHERE date = ?
            ''', (today,))
        elif action == 'completed':
            cursor.execute('''
                UPDATE daily_stats 
                SET tasks_completed = tasks_completed + 1
                WHERE date = ?
            ''', (today,))

        # Calculate completion rate
        cursor.execute('''
            UPDATE daily_stats
            SET completion_rate = CAST(tasks_completed AS REAL) / NULLIF(tasks_created, 0) * 100
            WHERE date = ?
        ''', (today,))

        conn.commit()
        conn.close()

    def get_daily_stats(self, date=None):
        """Get statistics for a specific date (LIVE data)"""
        if not date:
            date = datetime.now().date().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
        stats = cursor.fetchone()
        conn.close()
        return stats

    def get_weekly_stats(self):
        """Get statistics for the past 7 days (LIVE data)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get last 7 days
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

        stats = []
        for date in dates:
            cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
            day_stats = cursor.fetchone()
            if day_stats:
                stats.append(day_stats)
            else:
                # Return zeros for days with no data
                stats.append((None, date, 0, 0, 0, 0))

        conn.close()
        return stats

    def get_completion_rate(self):
        """Calculate LIVE completion rate from actual data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get all-time stats
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tasks')
        total = cursor.fetchone()[0]

        conn.close()

        if total == 0:
            return 0
        return (completed / total * 100)

    def get_today_completion_rate(self):
        """Get today's completion rate (LIVE)"""
        today = datetime.now().date().isoformat()
        stats = self.get_daily_stats(today)

        if stats and stats[2] > 0:  # tasks_created > 0
            return stats[4]  # completion_rate
        return 0

    # ==================== REMINDERS ====================

    def get_pending_reminders(self):
        """Get reminders that need to be sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            SELECT r.*, t.title, t.motivational_quote
            FROM task_reminders r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.sent = 0 
            AND r.reminder_time <= ?
            AND t.status = 'pending'
            ORDER BY r.reminder_time ASC
        ''', (now,))

        reminders = cursor.fetchall()
        conn.close()
        return reminders

    def mark_reminder_sent(self, reminder_id):
        """Mark a reminder as sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE task_reminders SET sent = 1 WHERE id = ?
        ''', (reminder_id,))
        conn.commit()
        conn.close()

    # ==================== GOALS (existing) ====================

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

    # ==================== TIME TRACKING ====================

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