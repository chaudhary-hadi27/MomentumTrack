from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp


class TaskItem(MDBoxLayout):
    task_id = NumericProperty(0)
    task_title = StringProperty("")
    task_notes = StringProperty("")
    task_start_time = StringProperty("")
    task_end_time = StringProperty("")
    task_recurrence = StringProperty("")
    task_completed = BooleanProperty(False)
    is_subtask = BooleanProperty(False)
    on_task_click = ObjectProperty(None)
    on_toggle_complete = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(90 if self.task_start_time or self.task_recurrence else 70)
        self.padding = [dp(12) if not self.is_subtask else dp(40), dp(8), dp(8), dp(8)]
        self.spacing = dp(12)

        # Add card-like background that adapts to theme
        with self.canvas.before:
            self.bg_color = Color(0.98, 0.98, 0.98, 1)  # Will be updated based on theme
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.update_theme_colors()

        self.build_ui()

    def update_theme_colors(self):
        """Update colors based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls:
            if app.theme_cls.theme_style == "Dark":
                # Dark theme: slightly lighter than background
                self.bg_color.rgba = (0.15, 0.15, 0.15, 1)
            else:
                # Light theme: light gray
                self.bg_color.rgba = (0.98, 0.98, 0.98, 1)

    def _update_rect(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def build_ui(self):
        # Modern checkbox
        self.checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            active=self.task_completed,
            color_active=(0.1, 0.45, 0.91, 1),
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
            theme_text_color="Primary" if not self.task_completed else "Hint",
            strikethrough=self.task_completed,
            size_hint_y=None,
            height=dp(28),
            bold=True
        )
        content_layout.add_widget(self.title_label)

        # Time info (if exists)
        if self.task_start_time or self.task_end_time:
            time_text = ""
            if self.task_start_time and self.task_end_time:
                time_text = f"🕐 {self.task_start_time} - {self.task_end_time}"
            elif self.task_start_time:
                time_text = f"🕐 Starts at {self.task_start_time}"

            if time_text:
                self.time_label = MDLabel(
                    text=time_text,
                    font_style="Caption",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(18)
                )
                content_layout.add_widget(self.time_label)

        # Recurrence info (if exists)
        if self.task_recurrence:
            recurrence_icons = {
                "today": "🔄 Daily",
                "week": "🔄 Weekly",
                "month": "🔄 Monthly",
                "year": "🔄 Yearly",
                "custom": "🔄 Custom"
            }
            recurrence_text = recurrence_icons.get(self.task_recurrence, "🔄 Repeating")

            self.recurrence_label = MDLabel(
                text=recurrence_text,
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(18)
            )
            content_layout.add_widget(self.recurrence_label)

        self.add_widget(content_layout)

        # Delete button
        delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Hint",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=self.on_delete_click
        )
        self.add_widget(delete_btn)

    def on_checkbox_active(self, checkbox, value):
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task_id, value)
        self.update_completed_style(value)

    def update_completed_style(self, completed):
        self.task_completed = completed
        self.title_label.theme_text_color = "Hint" if completed else "Primary"
        self.title_label.strikethrough = completed

    def on_delete_click(self, *args):
        if self.on_delete:
            self.on_delete(self.task_id)

    def on_touch_down(self, touch):
        # Check if touch is not on checkbox or delete button
        if self.collide_point(*touch.pos):
            for child in self.children:
                if child.collide_point(*touch.pos):
                    if isinstance(child, (MDCheckbox, MDIconButton)):
                        return super().on_touch_down(touch)

            # Touch is on task content area
            if self.on_task_click:
                self.on_task_click(self.task_id)
            return True
        return super().on_touch_down(touch)