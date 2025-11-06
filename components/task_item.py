from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from utils.constants import Colors


class TaskItem(MDBoxLayout):
    task_id = NumericProperty(0)
    task_title = StringProperty("")
    task_notes = StringProperty("")
    task_start_time = StringProperty("")
    task_end_time = StringProperty("")
    task_recurrence = StringProperty("")
    task_motivation = StringProperty("")
    task_completed = BooleanProperty(False)
    is_subtask = BooleanProperty(False)
    on_task_click = ObjectProperty(None)
    on_toggle_complete = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None

        # Calculate height based on content
        base_height = 70
        if self.task_start_time or self.task_recurrence:
            base_height += 20
        if self.task_motivation:
            base_height += 20

        self.height = dp(base_height)
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

    def update_theme_colors(self):
        """Update colors based on current theme - optimized"""
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
        delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Hint",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=self.on_delete_click
        )
        self.add_widget(delete_btn)

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
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task_id, value)
        self.update_completed_style(value)

    def update_completed_style(self, completed):
        """Update visual style for completion status"""
        self.task_completed = completed
        self.title_label.strikethrough = completed

        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            self._update_label_colors(is_dark)

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