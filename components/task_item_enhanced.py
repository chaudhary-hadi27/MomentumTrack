from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivymd.app import MDApp
from utils.constants import Colors
from utils.gesture_handler import GestureHandler
import time


class TaskItemEnhanced(MDBoxLayout):
    """Enhanced task item with gesture support and animations"""

    task_id = NumericProperty(0)
    task_title = StringProperty("")
    task_notes = StringProperty("")
    task_start_time = StringProperty("")
    task_end_time = StringProperty("")
    task_recurrence = StringProperty("")
    task_motivation = StringProperty("")
    task_completed = BooleanProperty(False)
    is_subtask = BooleanProperty(False)

    # Callbacks
    on_task_click = ObjectProperty(None)
    on_toggle_complete = ObjectProperty(None)
    on_delete = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_duplicate = ObjectProperty(None)

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

        # Swipe state
        self.original_x = 0
        self.swiped_state = None  # 'left' or 'right' or None
        self.last_tap_time = 0

        # Background
        with self.canvas.before:
            self.bg_color = Color(*Colors.LIGHT_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)

        # Setup gesture handler
        self.gesture_handler = GestureHandler(self, callbacks={
            'on_tap': self._on_tap,
            'on_long_press': self._on_long_press,
            'on_swipe_left': self._on_swipe_left,
            'on_swipe_right': self._on_swipe_right,
            'on_swipe_move': self._on_swipe_move
        })

        self.update_theme_colors()
        self.build_ui()

    def update_theme_colors(self):
        """Update colors based on current theme"""
        if not hasattr(self, 'bg_color'):
            return

        app = MDApp.get_running_app()
        if not app or not app.theme_cls:
            return

        is_dark = app.theme_cls.theme_style == "Dark"
        self.bg_color.rgba = Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD

        if hasattr(self, 'title_label'):
            self._update_label_colors(is_dark)

    def _update_label_colors(self, is_dark):
        """Update label colors"""
        if self.task_completed:
            self.title_label.color = (0.5, 0.5, 0.5, 1)
        else:
            self.title_label.color = Colors.DARK_TEXT if is_dark else Colors.LIGHT_TEXT

        secondary_color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT

        if hasattr(self, 'time_label'):
            self.time_label.color = secondary_color
        if hasattr(self, 'recurrence_label'):
            self.recurrence_label.color = secondary_color
        if hasattr(self, 'motivation_label'):
            self.motivation_label.color = (0.1, 0.6, 0.3, 1)

    def _update_rect(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def build_ui(self):
        """Build UI components"""
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

        # Task content
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4)
        )

        # Title with animation support
        self.title_label = MDLabel(
            text=self.task_title,
            font_style="Body1",
            strikethrough=self.task_completed,
            size_hint_y=None,
            height=dp(28),
            bold=True
        )

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
            if app and app.theme_cls:
                is_dark = app.theme_cls.theme_style == "Dark"
                self.recurrence_label.color = Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT
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

        # Delete button (hidden initially, shown on swipe)
        self.delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=Colors.DANGER_RED,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=self.on_delete_click,
            opacity=0
        )
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

    # Gesture handlers

    def _on_tap(self, touch):
        """Handle tap - check for double tap"""
        current_time = time.time()

        # Double tap to complete
        if current_time - self.last_tap_time < 0.3:
            if self.on_toggle_complete:
                self.on_toggle_complete(self.task_id, not self.task_completed)
                self._animate_complete()
            self.last_tap_time = 0
        else:
            # Single tap - open details
            if self.on_task_click:
                self.on_task_click(self.task_id)
            self.last_tap_time = current_time

    def _on_long_press(self, touch):
        """Handle long press - show context menu"""
        if self.on_edit:
            self.on_edit(self.task_id)

    def _on_swipe_left(self):
        """Handle swipe left - show delete"""
        self._show_delete_button()

    def _on_swipe_right(self):
        """Handle swipe right - complete task"""
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task_id, not self.task_completed)
            self._animate_complete()
            # Reset position
            self._reset_position()

    def _on_swipe_move(self, dx):
        """Handle swipe movement"""
        # Move the item
        max_swipe = dp(80)
        new_x = max(-max_swipe, min(max_swipe, dx))
        self.x = self.original_x + new_x

        # Show/hide delete button based on swipe
        if new_x < -dp(20):
            self.delete_btn.opacity = min(1, abs(new_x) / max_swipe)
        else:
            self.delete_btn.opacity = 0

    def _show_delete_button(self):
        """Animate showing delete button"""
        self.swiped_state = 'left'

        # Animate item and button
        anim_item = Animation(x=self.original_x - dp(80), duration=0.2, t='out_cubic')
        anim_btn = Animation(opacity=1, duration=0.2)

        anim_item.start(self)
        anim_btn.start(self.delete_btn)

    def _reset_position(self):
        """Reset item to original position"""
        self.swiped_state = None

        anim_item = Animation(x=self.original_x, duration=0.2, t='out_cubic')
        anim_btn = Animation(opacity=0, duration=0.2)

        anim_item.start(self)
        anim_btn.start(self.delete_btn)

    def _animate_complete(self):
        """Animate task completion"""
        if self.task_completed:
            # Fade in animation
            self.opacity = 0.5
            anim = Animation(opacity=1, duration=0.3)
            anim.start(self)
        else:
            # Scale animation
            original_height = self.height
            anim = Animation(height=original_height * 0.95, duration=0.15) + \
                   Animation(height=original_height, duration=0.15)
            anim.start(self)

    # Event handlers

    def on_checkbox_active(self, checkbox, value):
        """Handle checkbox toggle"""
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task_id, value)
        self.update_completed_style(value)

    def update_completed_style(self, completed):
        """Update visual style for completion"""
        self.task_completed = completed
        self.title_label.strikethrough = completed

        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            self._update_label_colors(is_dark)

    def on_delete_click(self, *args):
        """Handle delete button click"""
        if self.on_delete:
            self.on_delete(self.task_id)

    # Touch events

    def on_touch_down(self, touch):
        """Handle touch down"""
        if self.collide_point(*touch.pos):
            # Store original position
            self.original_x = self.x

            # Check if touching checkbox or delete button
            for child in self.children:
                if child.collide_point(*touch.pos):
                    if isinstance(child, (MDCheckbox, MDIconButton)):
                        return super().on_touch_down(touch)

            # Handle with gesture handler
            if self.gesture_handler.on_touch_down(touch):
                return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Handle touch move"""
        if self.gesture_handler.on_touch_move(touch):
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        """Handle touch up"""
        if self.gesture_handler.on_touch_up(touch):
            return True
        return super().on_touch_up(touch)