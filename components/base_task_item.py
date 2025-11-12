"""
Base Task Item Component - Eliminates code duplication
Used for both regular tasks and recycled tasks in virtual lists
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from utils.constants import Colors


class BaseTaskItem(MDBoxLayout):
    """
    Base task item widget with all common functionality.
    Can be used directly or subclassed for RecycleView.
    """

    task_id = NumericProperty(0)
    task_title = StringProperty("")
    task_notes = StringProperty("")
    task_start_time = StringProperty("")
    task_end_time = StringProperty("")
    task_recurrence = StringProperty("")
    task_motivation = StringProperty("")
    task_completed = BooleanProperty(False)
    is_subtask = BooleanProperty(False)

    def __init__(self, on_task_click=None, on_toggle_complete=None, on_delete=None, **kwargs):
        # Store callbacks as instance variables BEFORE calling super().__init__
        self._on_task_click = on_task_click
        self._on_toggle_complete = on_toggle_complete
        self._on_delete = on_delete

        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None

        # Calculate height based on content
        self.height = self._calculate_height()

        self.padding = [dp(12) if not self.is_subtask else dp(40), dp(8), dp(8), dp(8)]
        self.spacing = dp(12)

        # Add card-like background
        with self.canvas.before:
            self.bg_color = Color(*Colors.LIGHT_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.update_theme_colors()
        self.build_ui()

    def _calculate_height(self):
        """Calculate item height based on content"""
        base_height = 70
        if self.task_start_time or self.task_recurrence:
            base_height += 20
        if self.task_motivation:
            base_height += 20
        return dp(base_height)

    def set_callbacks(self, on_task_click=None, on_toggle_complete=None, on_delete=None):
        """Update callbacks after initialization (useful for RecycleView)"""
        if on_task_click:
            self._on_task_click = on_task_click
        if on_toggle_complete:
            self._on_toggle_complete = on_toggle_complete
        if on_delete:
            self._on_delete = on_delete

    def update_data(self, task_data):
        """Update task data (useful for RecycleView refresh)"""
        self.task_id = task_data.get('task_id', 0)
        self.task_title = task_data.get('task_title', "")
        self.task_notes = task_data.get('task_notes', "")
        self.task_start_time = task_data.get('task_start_time', "")
        self.task_end_time = task_data.get('task_end_time', "")
        self.task_recurrence = task_data.get('task_recurrence', "")
        self.task_motivation = task_data.get('task_motivation', "")
        self.task_completed = task_data.get('task_completed', False)
        self.is_subtask = task_data.get('is_subtask', False)

        # Update callbacks
        self.set_callbacks(
            on_task_click=task_data.get('on_task_click'),
            on_toggle_complete=task_data.get('on_toggle_complete'),
            on_delete=task_data.get('on_delete')
        )

        # Recalculate height and rebuild
        self.height = self._calculate_height()
        self.clear_widgets()
        self.build_ui()
        self.update_theme_colors()

    def update_theme_colors(self):
        """Update colors based on current theme"""
        if not hasattr(self, 'bg_color'):
            return

        app = MDApp.get_running_app()
        if not app or not app.theme_cls:
            return

        is_dark = app.theme_cls.theme_style == "Dark"

        # Update background
        self.bg_color.rgba = Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD

        # Update text colors if labels exist
        if hasattr(self, 'title_label'):
            self._update_label_colors(is_dark)

    def _update_label_colors(self, is_dark):
        """Internal method to update label colors"""
        if self.task_completed:
            self.title_label.color = (0.5, 0.5, 0.5, 1)
        else:
            self.title_label.color = Colors.DARK_TEXT if is_dark else Colors.LIGHT_TEXT

        # Update secondary labels
        secondary_color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT

        if hasattr(self, 'time_label'):
            self.time_label.color = secondary_color
        if hasattr(self, 'recurrence_label'):
            self.recurrence_label.color = secondary_color
        if hasattr(self, 'motivation_label'):
            self.motivation_label.color = (0.1, 0.6, 0.3, 1)  # Green for motivation

    def _update_rect(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def build_ui(self):
        """Build the UI components"""
        # Modern checkbox
        self.checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            active=self.task_completed,
            color_active=Colors.PRIMARY_BLUE,
            color_inactive=(0.5, 0.5, 0.5, 0.6)
        )
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.checkbox)

        # Task content
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

        # Set initial color
        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            if self.task_completed:
                self.title_label.color = (0.5, 0.5, 0.5, 1)
            else:
                self.title_label.color = Colors.DARK_TEXT if is_dark else Colors.LIGHT_TEXT

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

                # Set color
                if app and app.theme_cls:
                    is_dark = app.theme_cls.theme_style == "Dark"
                    self.time_label.color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT

                content_layout.add_widget(self.time_label)

        # Recurrence info
        if self.task_recurrence:
            recurrence_text = self._get_recurrence_text()
            self.recurrence_label = MDLabel(
                text=recurrence_text,
                font_style="Caption",
                size_hint_y=None,
                height=dp(18)
            )

            # Set color
            if app and app.theme_cls:
                is_dark = app.theme_cls.theme_style == "Dark"
                self.recurrence_label.color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT

            content_layout.add_widget(self.recurrence_label)

        # Motivation info
        if self.task_motivation:
            self.motivation_label = MDLabel(
                text=f"💪 {self.task_motivation}",
                font_style="Caption",
                size_hint_y=None,
                height=dp(18),
                color=(0.1, 0.6, 0.3, 1),  # Green color
                italic=True
            )
            content_layout.add_widget(self.motivation_label)

        self.add_widget(content_layout)

        # Delete button
        self.delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=Colors.DANGER_RED,
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.delete_btn.bind(on_release=self.on_delete_click)
        self.add_widget(self.delete_btn)

    def _get_time_text(self):
        """Get formatted time text"""
        if self.task_start_time and self.task_end_time:
            return f"🕐 {self.task_start_time} - {self.task_end_time}"
        elif self.task_start_time:
            return f"🕐 Starts at {self.task_start_time}"
        return ""

    def _get_recurrence_text(self):
        """Get formatted recurrence text"""
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
        self.update_completed_style(value)

    def update_completed_style(self, completed):
        """Update visual style for completion status"""
        self.task_completed = completed
        self.title_label.strikethrough = completed

        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            self._update_label_colors(is_dark)

    def on_delete_click(self, button_instance):
        """Handle delete button click"""
        if self._on_delete:
            self._on_delete(self.task_id)
        else:
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

            # Touch is on task content area - open details
            if self._on_task_click:
                self._on_task_click(self.task_id)
            return True
        return super().on_touch_down(touch)