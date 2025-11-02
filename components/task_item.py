from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80 if self.task_start_time or self.task_recurrence else 60)
        self.padding = [dp(16) if not self.is_subtask else dp(48), dp(8), dp(16), dp(8)]
        self.spacing = dp(12)

        self.build_ui()

    def build_ui(self):
        # Checkbox
        self.checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            active=self.task_completed
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
            height=dp(24)
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
                    height=dp(16)
                )
                content_layout.add_widget(self.time_label)

        # Recurrence info (if exists)
        if self.task_recurrence:
            recurrence_icons = {
                "today": "📅 Daily",
                "week": "📅 Weekly",
                "month": "📅 Monthly",
                "year": "📅 Yearly",
                "custom": "📅 Custom"
            }
            recurrence_text = recurrence_icons.get(self.task_recurrence, "📅 Repeating")

            self.recurrence_label = MDLabel(
                text=recurrence_text,
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(16)
            )
            content_layout.add_widget(self.recurrence_label)

        self.add_widget(content_layout)

    def on_checkbox_active(self, checkbox, value):
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task_id, value)
        self.update_completed_style(value)

    def update_completed_style(self, completed):
        self.task_completed = completed
        self.title_label.theme_text_color = "Hint" if completed else "Primary"
        self.title_label.strikethrough = completed

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.checkbox.collide_point(*touch.pos):
            if self.on_task_click:
                self.on_task_click(self.task_id)
            return True
        return super().on_touch_down(touch)