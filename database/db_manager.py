import sqlite3
from datetime import datetime
from utils.constants import DB_NAME, DEFAULT_LIST_NAME
from database.models import Task, TaskList


class DatabaseManager:
    def __init__(self):
        self.db_name = DB_NAME
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create task_lists table with position
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create tasks table with enhanced fields
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (list_id) REFERENCES task_lists (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()

        # Create default list if none exists
        cursor.execute('SELECT COUNT(*) FROM task_lists')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO task_lists (name, position) VALUES (?, ?)', (DEFAULT_LIST_NAME, 0))
            conn.commit()

        conn.close()

    # ===== TASK LIST OPERATIONS =====

    def get_all_lists(self):
        """Get all task lists ordered by position"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, position, created_at FROM task_lists ORDER BY position')
        rows = cursor.fetchall()
        conn.close()

        return [TaskList(id=row[0], name=row[1], position=row[2], created_at=row[3]) for row in rows]

    def get_list_by_id(self, list_id):
        """Get a specific task list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, position, created_at FROM task_lists WHERE id = ?', (list_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return TaskList(id=row[0], name=row[1], position=row[2], created_at=row[3])
        return None

    def create_list(self, name):
        """Create a new task list"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get max position
        cursor.execute('SELECT MAX(position) FROM task_lists')
        max_pos = cursor.fetchone()[0] or 0

        cursor.execute('INSERT INTO task_lists (name, position) VALUES (?, ?)', (name, max_pos + 1))
        list_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return list_id

    def update_list(self, list_id, name):
        """Update task list name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE task_lists SET name = ? WHERE id = ?', (name, list_id))
        conn.commit()
        conn.close()

    def delete_list(self, list_id):
        """Delete a task list and all its tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM task_lists WHERE id = ?', (list_id,))
        conn.commit()
        conn.close()

    def reorder_lists(self, list_ids):
        """Reorder lists"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for position, list_id in enumerate(list_ids):
            cursor.execute('UPDATE task_lists SET position = ? WHERE id = ?', (position, list_id))

        conn.commit()
        conn.close()

    # ===== TASK OPERATIONS =====

    def get_tasks_by_list(self, list_id, show_completed=True):
        """Get all tasks for a specific list"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT id, list_id, title, notes, due_date, start_time, end_time, 
                   reminder_time, completed, parent_id, position, recurrence_type,
                   recurrence_interval, last_completed_date, created_at
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
            task = Task(
                id=row[0], list_id=row[1], title=row[2], notes=row[3],
                due_date=row[4], start_time=row[5], end_time=row[6],
                reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                last_completed_date=row[13], created_at=row[14]
            )

            # Only show if it should appear today
            if task.should_show_today():
                task.subtasks = self.get_subtasks(task.id)
                tasks.append(task)

        conn.close()
        return tasks

    def get_subtasks(self, parent_id):
        """Get all subtasks for a parent task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, list_id, title, notes, due_date, start_time, end_time,
                   reminder_time, completed, parent_id, position, recurrence_type,
                   recurrence_interval, last_completed_date, created_at
            FROM tasks
            WHERE parent_id = ?
            ORDER BY position ASC, created_at DESC
        ''', (parent_id,))
        rows = cursor.fetchall()
        conn.close()

        return [Task(
            id=row[0], list_id=row[1], title=row[2], notes=row[3],
            due_date=row[4], start_time=row[5], end_time=row[6],
            reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
            position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
            last_completed_date=row[13], created_at=row[14]
        ) for row in rows]

    def get_task_by_id(self, task_id):
        """Get a specific task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, list_id, title, notes, due_date, start_time, end_time,
                   reminder_time, completed, parent_id, position, recurrence_type,
                   recurrence_interval, last_completed_date, created_at
            FROM tasks WHERE id = ?
        ''', (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            task = Task(
                id=row[0], list_id=row[1], title=row[2], notes=row[3],
                due_date=row[4], start_time=row[5], end_time=row[6],
                reminder_time=row[7], completed=bool(row[8]), parent_id=row[9],
                position=row[10], recurrence_type=row[11], recurrence_interval=row[12],
                last_completed_date=row[13], created_at=row[14]
            )
            task.subtasks = self.get_subtasks(task.id)
            return task
        return None

    def create_task(self, list_id, title, notes="", due_date=None, start_time=None,
                    end_time=None, reminder_time=None, parent_id=None,
                    recurrence_type=None, recurrence_interval=1):
        """Create a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get next position
        if parent_id:
            cursor.execute('SELECT MAX(position) FROM tasks WHERE parent_id = ?', (parent_id,))
        else:
            cursor.execute('SELECT MAX(position) FROM tasks WHERE list_id = ? AND parent_id IS NULL', (list_id,))

        max_position = cursor.fetchone()[0]
        position = (max_position or 0) + 1

        cursor.execute('''
            INSERT INTO tasks (list_id, title, notes, due_date, start_time, end_time,
                             reminder_time, parent_id, position, recurrence_type, recurrence_interval)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (list_id, title, notes, due_date, start_time, end_time,
              reminder_time, parent_id, position, recurrence_type, recurrence_interval))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def update_task(self, task_id, **kwargs):
        """Update task details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        allowed_fields = ['title', 'notes', 'due_date', 'start_time', 'end_time',
                          'reminder_time', 'completed', 'recurrence_type',
                          'recurrence_interval', 'last_completed_date']

        for field in allowed_fields:
            if field in kwargs:
                updates.append(f'{field} = ?')
                values.append(kwargs[field])

        if updates:
            values.append(task_id)
            query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, values)
            conn.commit()

        conn.close()

    def toggle_task_completed(self, task_id):
        """Toggle task completion status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT completed, recurrence_type FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()

        if row:
            current = row[0]
            recurrence_type = row[1]
            new_status = 0 if current else 1

            # If completing a recurring task, update last_completed_date
            if new_status == 1 and recurrence_type:
                today = datetime.now().date().isoformat()
                cursor.execute('UPDATE tasks SET completed = ?, last_completed_date = ? WHERE id = ?',
                               (new_status, today, task_id))
            else:
                cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))

            conn.commit()
            conn.close()
            return bool(new_status)

        conn.close()
        return False

    def delete_task(self, task_id):
        """Delete a task and all its subtasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    def get_tasks_with_reminders_today(self):
        """Get all tasks that have reminders for today"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date().isoformat()

        cursor.execute('''
            SELECT id, list_id, title, start_time, end_time, reminder_time
            FROM tasks
            WHERE due_date = ? AND reminder_time IS NOT NULL AND completed = 0
        ''', (today,))

        rows = cursor.fetchall()
        conn.close()
        return rows