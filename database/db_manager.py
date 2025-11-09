import sqlite3
from datetime import datetime
from functools import lru_cache
from contextlib import contextmanager
from utils.constants import DB_NAME, DEFAULT_LIST_NAME
from database.models import Task, TaskList, TaskCategory


class DatabaseManager:
    def __init__(self):
        self.db_name = DB_NAME
        self._connection_pool = []
        self.init_database()

    @contextmanager
    def get_connection_context(self):
        """Context manager for database connections with proper cleanup"""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()

    def get_connection(self):
        """Get database connection - use get_connection_context() instead when possible"""
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            # Create task_lists table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT 'daily',
                    position INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Migration: Add category column if it doesn't exist
            cursor.execute("PRAGMA table_info(task_lists)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'category' not in columns:
                print("🔄 Migrating database: Adding category column...")
                cursor.execute('ALTER TABLE task_lists ADD COLUMN category TEXT DEFAULT "daily"')
                cursor.execute('UPDATE task_lists SET category = "daily" WHERE category IS NULL')
                print("✅ Database migration complete!")

            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    notes TEXT,
                    due_date DATE,
                    start_time TIME,
                    end_time TIME,
                    reminder_time TIME,
                    completed BOOLEAN DEFAULT 0,
                    parent_id INTEGER,
                    position INTEGER DEFAULT 0,
                    recurrence_type TEXT,
                    recurrence_interval INTEGER DEFAULT 1,
                    last_completed_date DATE,
                    motivation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (list_id) REFERENCES task_lists (id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES tasks (id) ON DELETE CASCADE
                )
            ''')

            # Migration: Add motivation column if it doesn't exist
            cursor.execute("PRAGMA table_info(tasks)")
            task_columns = [column[1] for column in cursor.fetchall()]

            if 'motivation' not in task_columns:
                print("🔄 Migrating database: Adding motivation column...")
                cursor.execute('ALTER TABLE tasks ADD COLUMN motivation TEXT')
                print("✅ Motivation column added!")

            # Create default lists if none exist
            cursor.execute('SELECT COUNT(*) FROM task_lists')
            if cursor.fetchone()[0] == 0:
                print("📝 Creating default lists for each category...")
                for idx, cat in enumerate(TaskCategory.get_all()):
                    cursor.execute(
                        'INSERT INTO task_lists (name, category, position) VALUES (?, ?, ?)',
                        (f"My {cat['name']}", cat['id'], idx)
                    )
                print("✅ Default lists created!")

    def clear_cache(self):
        """Clear all cached data"""
        self.get_lists_by_category_cached.cache_clear()

    # ===== CATEGORY OPERATIONS =====

    @lru_cache(maxsize=8)
    def get_lists_by_category_cached(self, category):
        """Cached version of get_lists_by_category"""
        return self.get_lists_by_category(category)

    def get_lists_by_category(self, category):
        """Get all lists for a specific category"""
        if not TaskCategory.is_valid(category):
            raise ValueError(f"Invalid category: {category}")

        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, position, created_at 
                FROM task_lists 
                WHERE category = ?
                ORDER BY position
            ''', (category,))
            rows = cursor.fetchall()
            return [TaskList(id=row[0], name=row[1], category=row[2],
                             position=row[3], created_at=row[4]) for row in rows]

    def get_all_categories_with_lists(self):
        """Get all categories with their lists"""
        result = {}
        for cat in TaskCategory.get_all():
            result[cat['id']] = {
                'info': cat,
                'lists': self.get_lists_by_category(cat['id'])
            }
        return result

    # ===== TASK LIST OPERATIONS =====

    def get_all_lists(self):
        """Get all task lists ordered by category and position"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, position, created_at 
                FROM task_lists 
                ORDER BY 
                    CASE category
                        WHEN 'daily' THEN 1
                        WHEN 'weekend' THEN 2
                        WHEN 'monthly' THEN 3
                        WHEN 'yearly' THEN 4
                    END, position
            ''')
            rows = cursor.fetchall()
            return [TaskList(id=row[0], name=row[1], category=row[2],
                             position=row[3], created_at=row[4]) for row in rows]

    def get_list_by_id(self, list_id):
        """Get a specific task list"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, position, created_at 
                FROM task_lists WHERE id = ?
            ''', (list_id,))
            row = cursor.fetchone()

            if row:
                return TaskList(id=row[0], name=row[1], category=row[2],
                                position=row[3], created_at=row[4])
            return None

    def create_list(self, name, category="daily"):
        """Create a new task list in a category"""
        if not TaskCategory.is_valid(category):
            raise ValueError(f"Invalid category: {category}")

        # Validate name using TaskList validation
        try:
            TaskList(name=name, category=category)
        except ValueError as e:
            raise ValueError(f"Invalid list name: {e}")

        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            # Get max position for this category
            cursor.execute('''
                SELECT MAX(position) FROM task_lists WHERE category = ?
            ''', (category,))
            max_pos = cursor.fetchone()[0] or 0

            cursor.execute('''
                INSERT INTO task_lists (name, category, position) 
                VALUES (?, ?, ?)
            ''', (name.strip(), category, max_pos + 1))
            list_id = cursor.lastrowid

            # Clear cache
            self.clear_cache()

            return list_id

    def update_list(self, list_id, name):
        """Update task list name"""
        if not name or len(name) > 200:
            raise ValueError("Invalid list name")

        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE task_lists SET name = ? WHERE id = ?',
                           (name.strip(), list_id))
            # Clear cache
            self.clear_cache()

    def delete_list(self, list_id):
        """Delete a task list and all its tasks (with proper transaction)"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            # First delete all tasks (respects CASCADE)
            cursor.execute('DELETE FROM tasks WHERE list_id = ?', (list_id,))

            # Then delete the list
            cursor.execute('DELETE FROM task_lists WHERE id = ?', (list_id,))

            # Clear cache
            self.clear_cache()

    def cleanup_completed_daily_tasks(self):
        """Delete completed tasks from daily lists"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            # Get all daily list IDs
            cursor.execute("SELECT id FROM task_lists WHERE category = 'daily'")
            daily_list_ids = [row[0] for row in cursor.fetchall()]

            if daily_list_ids:
                placeholders = ','.join(['?' for _ in daily_list_ids])
                cursor.execute(f'''
                    DELETE FROM tasks 
                    WHERE list_id IN ({placeholders}) 
                    AND completed = 1
                ''', daily_list_ids)
                deleted_count = cursor.rowcount
                print(f"🧹 Cleaned up {deleted_count} completed daily tasks")

    # ===== TASK OPERATIONS =====

    def get_tasks_by_list(self, list_id, show_completed=True):
        """Get all tasks for a specific list"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT id, list_id, title, notes, due_date, start_time, end_time, 
                       reminder_time, completed, parent_id, position, recurrence_type,
                       recurrence_interval, last_completed_date, motivation, created_at
                FROM tasks
                WHERE list_id = ? AND parent_id IS NULL
            '''

            if not show_completed:
                query += ' AND completed = 0'

            query += ' ORDER BY completed ASC, position ASC, created_at DESC'

            cursor.execute(query, (list_id,))
            rows = cursor.fetchall()

            tasks = []
            for row in rows:
                try:
                    task = Task(
                        id=row[0], list_id=row[1], title=row[2], notes=row[3],
                        due_date=row[4], start_time=row[5], end_time=row[6],
                        reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                        position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                        last_completed_date=row[13], motivation=row[14] or "", created_at=row[15]
                    )
                    task.subtasks = self.get_subtasks(task.id)
                    tasks.append(task)
                except ValueError as e:
                    print(f"⚠️ Skipping invalid task {row[0]}: {e}")
                    continue

            return tasks

    def get_subtasks(self, parent_id):
        """Get all subtasks for a parent task"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, list_id, title, notes, due_date, start_time, end_time,
                       reminder_time, completed, parent_id, position, recurrence_type,
                       recurrence_interval, last_completed_date, motivation, created_at
                FROM tasks
                WHERE parent_id = ?
                ORDER BY position ASC, created_at DESC
            ''', (parent_id,))
            rows = cursor.fetchall()

            subtasks = []
            for row in rows:
                try:
                    task = Task(
                        id=row[0], list_id=row[1], title=row[2], notes=row[3],
                        due_date=row[4], start_time=row[5], end_time=row[6],
                        reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                        position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                        last_completed_date=row[13], motivation=row[14] or "", created_at=row[15]
                    )
                    subtasks.append(task)
                except ValueError as e:
                    print(f"⚠️ Skipping invalid subtask {row[0]}: {e}")
                    continue

            return subtasks

    def get_task_by_id(self, task_id):
        """Get a specific task"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, list_id, title, notes, due_date, start_time, end_time,
                       reminder_time, completed, parent_id, position, recurrence_type,
                       recurrence_interval, last_completed_date, motivation, created_at
                FROM tasks WHERE id = ?
            ''', (task_id,))
            row = cursor.fetchone()

            if row:
                try:
                    task = Task(
                        id=row[0], list_id=row[1], title=row[2], notes=row[3],
                        due_date=row[4], start_time=row[5], end_time=row[6],
                        reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                        position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                        last_completed_date=row[13], motivation=row[14] or "", created_at=row[15]
                    )
                    task.subtasks = self.get_subtasks(task.id)
                    return task
                except ValueError as e:
                    print(f"❌ Invalid task data: {e}")
                    return None
            return None

    def create_task(self, list_id, title, notes="", due_date=None, start_time=None,
                    end_time=None, reminder_time=None, parent_id=None,
                    recurrence_type=None, recurrence_interval=1, motivation=""):
        """Create a new task with all fields including motivation"""

        # Validate list exists
        list_obj = self.get_list_by_id(list_id)
        if not list_obj:
            raise ValueError(f"List with id {list_id} does not exist")

        # Validate using Task model
        try:
            Task(list_id=list_id, title=title, notes=notes,
                 start_time=start_time, end_time=end_time, motivation=motivation)
        except ValueError as e:
            raise ValueError(f"Invalid task data: {e}")

        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            if parent_id:
                cursor.execute('SELECT MAX(position) FROM tasks WHERE parent_id = ?', (parent_id,))
            else:
                cursor.execute('SELECT MAX(position) FROM tasks WHERE list_id = ? AND parent_id IS NULL', (list_id,))

            max_position = cursor.fetchone()[0]
            position = (max_position or 0) + 1

            cursor.execute('''
                INSERT INTO tasks (list_id, title, notes, due_date, start_time, end_time,
                                 reminder_time, parent_id, position, recurrence_type, 
                                 recurrence_interval, motivation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (list_id, title.strip(), notes, due_date, start_time, end_time,
                  reminder_time, parent_id, position, recurrence_type, recurrence_interval, motivation))

            task_id = cursor.lastrowid
            print(f"✅ Task created successfully: ID={task_id}, Title='{title}'")
            return task_id

    def update_task(self, task_id, **kwargs):
        """Update task details"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()

            updates = []
            values = []

            allowed_fields = ['title', 'notes', 'due_date', 'start_time', 'end_time',
                              'reminder_time', 'completed', 'recurrence_type',
                              'recurrence_interval', 'last_completed_date', 'motivation']

            for field in allowed_fields:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    value = kwargs[field]
                    # Strip strings
                    if isinstance(value, str):
                        value = value.strip()
                    values.append(value)

            if updates:
                values.append(task_id)
                query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)

    def toggle_task_completed(self, task_id):
        """Toggle task completion status"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()

            if row:
                new_status = 0 if row[0] else 1
                cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?',
                               (new_status, task_id))
                return bool(new_status)
            return False

    def delete_task(self, task_id):
        """Delete a task and all its subtasks"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

    def get_tasks_with_reminders_today(self):
        """Get all tasks that have reminders for today"""
        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            today = datetime.now().date().isoformat()

            cursor.execute('''
                SELECT id, list_id, title, start_time, end_time, reminder_time, motivation
                FROM tasks
                WHERE due_date = ? AND reminder_time IS NOT NULL AND completed = 0
            ''', (today,))

            return cursor.fetchall()

    def search_tasks(self, query):
        """Search tasks by title or notes"""
        if not query or len(query) < 2:
            return []

        with self.get_connection_context() as conn:
            cursor = conn.cursor()
            search_pattern = f'%{query}%'
            cursor.execute('''
                SELECT id, list_id, title, notes, due_date, start_time, end_time,
                       reminder_time, completed, parent_id, position, recurrence_type,
                       recurrence_interval, last_completed_date, motivation, created_at
                FROM tasks
                WHERE title LIKE ? OR notes LIKE ?
                ORDER BY completed ASC, created_at DESC
                LIMIT 50
            ''', (search_pattern, search_pattern))

            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                try:
                    task = Task(
                        id=row[0], list_id=row[1], title=row[2], notes=row[3],
                        due_date=row[4], start_time=row[5], end_time=row[6],
                        reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                        position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                        last_completed_date=row[13], motivation=row[14] or "", created_at=row[15]
                    )
                    tasks.append(task)
                except ValueError:
                    continue

            return tasks