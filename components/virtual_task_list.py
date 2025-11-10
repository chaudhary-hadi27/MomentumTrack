from kivymd.uix.recycleview import RecycleView
from kivymd.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from utils.constants import Colors


class RecyclableTaskItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable task item for virtual scrolling"""

    task_id = NumericProperty(0)
    task_title = StringProperty("")
    task_notes = StringProperty("")
    task_start_time = StringProperty("")
    task_end_time = StringProperty("")
    task_recurrence = StringProperty("")
    task_motivation = StringProperty("")
    task_completed = BooleanProperty(False)
    is_subtask = BooleanProperty(False)
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(90)
        self.padding = [dp(12), dp(8), dp(8), dp(8)]
        self.spacing = dp(12)

        # Store callbacks as instance variables
        self._on_task_click = None
        self._on_toggle_complete = None
        self._on_delete = None

        # Background
        with self.canvas.before:
            self.bg_color = Color(*Colors.LIGHT_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)

    def refresh_view_attrs(self, rv, index, data):
        """Called when data is updated"""
        self.index = index
        self.task_id = data.get('task_id', 0)
        self.task_title = data.get('task_title', "")
        self.task_notes = data.get('task_notes', "")
        self.task_start_time = data.get('task_start_time', "")
        self.task_end_time = data.get('task_end_time', "")
        self.task_recurrence = data.get('task_recurrence', "")
        self.task_motivation = data.get('task_motivation', "")
        self.task_completed = data.get('task_completed', False)
        self.is_subtask = data.get('is_subtask', False)

        # Store callbacks as instance variables
        self._on_task_click = data.get('on_task_click')
        self._on_toggle_complete = data.get('on_toggle_complete')
        self._on_delete = data.get('on_delete')

        print(f"✅ RecyclableTaskItem refresh: ID={self.task_id}, has_delete={self._on_delete is not None}")

        # Rebuild UI with new data
        self.clear_widgets()
        self.build_ui()
        self.update_theme_colors()

        return super().refresh_view_attrs(rv, index, data)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_theme_colors(self):
        """Update colors based on theme"""
        if not hasattr(self, 'bg_color'):
            return

        app = MDApp.get_running_app()
        if not app or not app.theme_cls:
            return

        is_dark = app.theme_cls.theme_style == "Dark"
        self.bg_color.rgba = Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD

        if hasattr(self, 'title_label'):
            if self.task_completed:
                self.title_label.color = (0.5, 0.5, 0.5, 1)
            else:
                self.title_label.color = Colors.DARK_TEXT if is_dark else Colors.LIGHT_TEXT

            secondary_color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT
            if hasattr(self, 'time_label'):
                self.time_label.color = secondary_color
            if hasattr(self, 'recurrence_label'):
                self.recurrence_label.color = secondary_color

    def build_ui(self):
        """Build the UI components"""
        # Checkbox
        self.checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            active=self.task_completed,
            color_active=Colors.PRIMARY_BLUE,
            color_inactive=(0.5, 0.5, 0.5, 0.6)
        )
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.checkbox)

        # Content
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4)
        )

        # Title
        self.title_label = MDLabel(
            text=self.task_title,
            font_style="Body1",
            strikethrough=self.task_completed,
            size_hint_y=None,
            height=dp(28),
            bold=True
        )
        content_layout.add_widget(self.title_label)

        # Time info
        if self.task_start_time or self.task_end_time:
            time_text = self._get_time_text()
            if time_text:
                self.time_label = MDLabel(
                    text=time_text,
                    font_style="Caption",
                    size_hint_y=None,
                    height=dp(18)
                )
                content_layout.add_widget(self.time_label)

        # Recurrence
        if self.task_recurrence:
            self.recurrence_label = MDLabel(
                text=self._get_recurrence_text(),
                font_style="Caption",
                size_hint_y=None,
                height=dp(18)
            )
            content_layout.add_widget(self.recurrence_label)

        # Motivation
        if self.task_motivation:
            self.motivation_label = MDLabel(
                text=f"💪 {self.task_motivation}",
                font_style="Caption",
                size_hint_y=None,
                height=dp(18),
                color=(0.1, 0.6, 0.3, 1),
                italic=True
            )
            content_layout.add_widget(self.motivation_label)

        self.add_widget(content_layout)

        # Delete button - Using instance variable callback
        self.delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=Colors.DANGER_RED,
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        # Bind directly to the button's on_release event
        self.delete_btn.bind(on_release=self.on_delete_click)
        self.add_widget(self.delete_btn)

    def _get_time_text(self):
        if self.task_start_time and self.task_end_time:
            return f"🕐 {self.task_start_time} - {self.task_end_time}"
        elif self.task_start_time:
            return f"🕐 Starts at {self.task_start_time}"
        return ""

    def _get_recurrence_text(self):
        recurrence_icons = {
            "today": "🔄 Daily",
            "week": "🔄 Weekly",
            "month": "🔄 Monthly",
            "year": "🔄 Yearly",
            "custom": "🔄 Custom"
        }
        return recurrence_icons.get(self.task_recurrence, "🔄 Repeating")

    def on_checkbox_active(self, checkbox, value):
        """Handle checkbox toggle"""
        if self._on_toggle_complete:
            self._on_toggle_complete(self.task_id, value)

    def on_delete_click(self, button_instance):
        """Handle delete button click - FIXED with instance variable"""
        print(f"🗑️ RecyclableTaskItem: Delete clicked for task {self.task_id}")
        print(f"🗑️ RecyclableTaskItem: Delete callback exists: {self._on_delete is not None}")

        if self._on_delete:
            print(f"🗑️ RecyclableTaskItem: Calling delete callback")
            self._on_delete(self.task_id)
        else:
            print(f"⚠️ RecyclableTaskItem: No delete callback set")
            from kivymd.toast import toast
            toast("Delete function not available")

    def on_touch_down(self, touch):
        """Handle touch events"""
        if self.collide_point(*touch.pos):
            # Check if touch is on checkbox
            if hasattr(self, 'checkbox') and self.checkbox.collide_point(*touch.pos):
                return super().on_touch_down(touch)

            # Check if touch is on delete button
            if hasattr(self, 'delete_btn') and self.delete_btn.collide_point(*touch.pos):
                return super().on_touch_down(touch)

            # Touch on task content - open details
            if self._on_task_click:
                self._on_task_click(self.task_id)
            return True
        return super().on_touch_down(touch)


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

        print(f"🔄 VirtualTaskList loading {len(tasks)} tasks")
        print(f"🔄 Callbacks: {list(callbacks.keys())}")
        print(f"🔄 on_delete callback exists: {callbacks.get('on_delete') is not None}")

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
        print(f"✅ VirtualTaskList loaded {len(self.data)} items")

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