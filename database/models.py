from datetime import datetime, timedelta


class TaskList:
    def __init__(self, id=None, name="", position=0, created_at=None):
        self.id = id
        self.name = name
        self.position = position
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Task:
    def __init__(self, id=None, list_id=None, title="", notes="",
                 due_date=None, start_time=None, end_time=None,
                 reminder_time=None, completed=False, parent_id=None,
                 position=0, recurrence_type=None, recurrence_interval=1,
                 last_completed_date=None, created_at=None):
        self.id = id
        self.list_id = list_id
        self.title = title
        self.notes = notes
        self.due_date = due_date
        self.start_time = start_time  # Time when task starts
        self.end_time = end_time  # Time when task ends
        self.reminder_time = reminder_time  # When to remind (between start and end)
        self.completed = completed
        self.parent_id = parent_id
        self.position = position
        self.recurrence_type = recurrence_type  # today, week, month, year, custom
        self.recurrence_interval = recurrence_interval  # For custom: every X days
        self.last_completed_date = last_completed_date  # Track when last completed
        self.created_at = created_at or datetime.now()
        self.subtasks = []

    def should_show_today(self):
        """Check if task should be shown today based on recurrence"""
        if not self.recurrence_type:
            return True

        if self.completed and self.last_completed_date:
            last_completed = datetime.strptime(self.last_completed_date, "%Y-%m-%d").date()
            today = datetime.now().date()

            if self.recurrence_type == "today":
                return last_completed < today
            elif self.recurrence_type == "week":
                return (today - last_completed).days >= 7
            elif self.recurrence_type == "month":
                return (today - last_completed).days >= 30
            elif self.recurrence_type == "year":
                return (today - last_completed).days >= 365
            elif self.recurrence_type == "custom":
                return (today - last_completed).days >= self.recurrence_interval

        return True

    def to_dict(self):
        return {
            'id': self.id,
            'list_id': self.list_id,
            'title': self.title,
            'notes': self.notes,
            'due_date': self.due_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reminder_time': self.reminder_time,
            'completed': self.completed,
            'parent_id': self.parent_id,
            'position': self.position,
            'recurrence_type': self.recurrence_type,
            'recurrence_interval': self.recurrence_interval,
            'last_completed_date': self.last_completed_date,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }