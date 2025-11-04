from datetime import datetime, timedelta


class TaskCategory:
    """Time-based categories for organizing lists"""
    DAILY = "daily"
    WEEKEND = "weekend"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @staticmethod
    def get_all():
        return [
            {"id": TaskCategory.DAILY, "name": "Daily Tasks", "icon": "🗓️"},
            {"id": TaskCategory.WEEKEND, "name": "Weekend Tasks", "icon": "📅"},
            {"id": TaskCategory.MONTHLY, "name": "Monthly Goals", "icon": "📆"},
            {"id": TaskCategory.YEARLY, "name": "Yearly Goals", "icon": "🎯"}
        ]


class TaskList:
    def __init__(self, id=None, name="", category="daily", position=0, created_at=None):
        self.id = id
        self.name = name
        self.category = category  # daily, weekend, monthly, yearly
        self.position = position
        self.created_at = created_at or datetime.now()

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
                 last_completed_date=None, created_at=None):
        self.id = id
        self.list_id = list_id
        self.title = title
        self.notes = notes
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
        self.created_at = created_at or datetime.now()
        self.subtasks = []

    def should_show_today(self):
        """Check if task should be shown based on list category and completion"""
        if not self.completed:
            return True

        # For daily tasks, hide completed tasks immediately
        # They will be auto-deleted at day end
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
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }