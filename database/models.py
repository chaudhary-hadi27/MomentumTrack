from datetime import datetime, timedelta
from utils.constants import TIME_FORMAT


class TaskCategory:
    """Time-based categories for organizing lists"""
    DAILY = "daily"
    WEEKEND = "weekend"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @staticmethod
    def get_all():
        return [
            {"id": TaskCategory.DAILY, "name": "Daily Tasks"},
            {"id": TaskCategory.WEEKEND, "name": "Weekend Tasks"},
            {"id": TaskCategory.MONTHLY, "name": "Monthly Goals"},
            {"id": TaskCategory.YEARLY, "name": "Yearly Goals"}
        ]

    @staticmethod
    def is_valid(category):
        """Check if category is valid"""
        return category in [c['id'] for c in TaskCategory.get_all()]


class TaskList:
    def __init__(self, id=None, name="", category="daily", position=0, created_at=None):
        self.id = id
        self.name = self._validate_name(name)
        self.category = category
        self.position = position
        self.created_at = created_at or datetime.now()

    def _validate_name(self, name):
        """Validate list name"""
        if not name or not name.strip():
            raise ValueError("List name cannot be empty")
        if len(name) > 200:
            raise ValueError("List name too long (max 200 characters)")
        return name.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'position': self.position,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Task:
    def __init__(self, id=None, list_id=None, title="", notes="",
                 due_date=None, start_time=None, end_time=None,
                 reminder_time=None, completed=False, parent_id=None,
                 position=0, recurrence_type=None, recurrence_interval=1,
                 last_completed_date=None, motivation="", created_at=None):
        self.id = id
        self.list_id = list_id
        self.title = self._validate_title(title)
        self.notes = self._validate_notes(notes)
        self.due_date = due_date
        self.start_time = start_time
        self.end_time = end_time
        self.reminder_time = reminder_time
        self.completed = completed
        self.parent_id = parent_id
        self.position = position
        self.recurrence_type = recurrence_type
        self.recurrence_interval = recurrence_interval
        self.last_completed_date = last_completed_date
        self.motivation = self._validate_motivation(motivation)
        self.created_at = created_at or datetime.now()
        self.subtasks = []

        # Validate time range
        self._validate_time_range()

    def _validate_title(self, title):
        """Validate task title"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > 500:
            raise ValueError("Task title too long (max 500 characters)")
        return title.strip()

    def _validate_notes(self, notes):
        """Validate task notes"""
        if notes and len(notes) > 5000:
            raise ValueError("Task notes too long (max 5000 characters)")
        return notes or ""

    def _validate_motivation(self, motivation):
        """Validate motivation message"""
        if motivation and len(motivation) > 500:
            raise ValueError("Motivation message too long (max 500 characters)")
        return motivation or ""

    def _validate_time_range(self):
        """Validate that end time is after start time"""
        if self.start_time and self.end_time:
            try:
                start = datetime.strptime(self.start_time, TIME_FORMAT)
                end = datetime.strptime(self.end_time, TIME_FORMAT)
                if end <= start:
                    raise ValueError("End time must be after start time")
            except ValueError as e:
                if "does not match format" in str(e):
                    raise ValueError("Invalid time format")
                raise

    def should_show_today(self):
        """Check if task should be shown based on list category and completion"""
        if not self.completed:
            return True
        # For daily tasks, hide completed tasks immediately
        return False

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
            'motivation': self.motivation,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }