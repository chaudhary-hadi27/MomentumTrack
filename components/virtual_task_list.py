"""
Virtual Task List - Now uses BaseTaskItem to eliminate duplication
"""

from kivymd.uix.recycleview import RecycleView
from kivymd.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.recycleboxlayout import RecycleBoxLayout
from kivy.metrics import dp
from components.base_task_item import BaseTaskItem


class RecyclableTaskItem(RecycleDataViewBehavior, BaseTaskItem):
    """
    Recyclable task item for virtual scrolling.
    Now extends BaseTaskItem instead of duplicating code!

    This eliminates ~250 lines of duplicate code!
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0

    def refresh_view_attrs(self, rv, index, data):
        """Called when data is updated - RecycleView specific"""
        self.index = index

        # Use the base class update_data method
        self.update_data(data)

        return super().refresh_view_attrs(rv, index, data)


class VirtualTaskList(RecycleView):
    """Virtual scrolling task list with recycled widgets"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.viewclass = 'RecyclableTaskItem'

        # Layout manager
        self.layout_manager = RecycleBoxLayout(
            default_size=(None, dp(90)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(8), dp(12)]
        )
        self.layout_manager.bind(minimum_height=self.layout_manager.setter('height'))
        self.add_widget(self.layout_manager)

        # Performance settings
        self.scroll_type = ['bars', 'content']
        self.bar_width = dp(8)
        self.effect_cls = 'ScrollEffect'  # Smooth scrolling

    def load_tasks(self, tasks, callbacks):
        """
        Load tasks into virtual list

        Args:
            tasks: List of Task objects
            callbacks: Dict with on_task_click, on_toggle_complete, on_delete
        """
        self.data = []

        for task in tasks:
            task_data = {
                'task_id': task.id,
                'task_title': task.title,
                'task_notes': task.notes or "",
                'task_start_time': task.start_time or "",
                'task_end_time': task.end_time or "",
                'task_recurrence': task.recurrence_type or "",
                'task_motivation': task.motivation or "",
                'task_completed': task.completed,
                'is_subtask': False,
                'on_task_click': callbacks.get('on_task_click'),
                'on_toggle_complete': callbacks.get('on_toggle_complete'),
                'on_delete': callbacks.get('on_delete')
            }
            self.data.append(task_data)

            # Add subtasks
            for subtask in task.subtasks:
                subtask_data = {
                    'task_id': subtask.id,
                    'task_title': subtask.title,
                    'task_notes': "",
                    'task_start_time': "",
                    'task_end_time': "",
                    'task_recurrence': "",
                    'task_motivation': "",
                    'task_completed': subtask.completed,
                    'is_subtask': True,
                    'on_task_click': callbacks.get('on_task_click'),
                    'on_toggle_complete': callbacks.get('on_toggle_complete'),
                    'on_delete': callbacks.get('on_delete')
                }
                self.data.append(subtask_data)

        self.refresh_from_data()

    def update_task_completion(self, task_id, completed):
        """Update specific task completion status"""
        for item in self.data:
            if item['task_id'] == task_id:
                item['task_completed'] = completed
                break
        self.refresh_from_data()

    def remove_task(self, task_id):
        """Remove task from list"""
        self.data = [item for item in self.data if item['task_id'] != task_id]
        self.refresh_from_data()