"""
Task Item - Now uses BaseTaskItem to eliminate duplication
"""

from components.base_task_item import BaseTaskItem


class TaskItem(BaseTaskItem):
    """
    Task item widget for regular (non-recycled) lists.
    Simply extends BaseTaskItem with no additional functionality needed.

    This eliminates ~200 lines of duplicate code!
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # All functionality is inherited from BaseTaskItem

    # That's it! No more duplicate code.
    # If you need TaskItem-specific behavior, add it here.