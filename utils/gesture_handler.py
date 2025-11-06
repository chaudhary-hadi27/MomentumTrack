from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
import time


class GestureHandler:
    """Handle touch gestures for tasks and lists"""

    SWIPE_THRESHOLD = dp(50)  # Minimum distance for swipe
    SWIPE_TIME_THRESHOLD = 0.5  # Maximum time for swipe (seconds)
    LONG_PRESS_DURATION = 0.5  # Long press duration (seconds)

    def __init__(self, widget, callbacks=None):
        self.widget = widget
        self.callbacks = callbacks or {}

        # Touch tracking
        self.touch_start_pos = None
        self.touch_start_time = None
        self.is_dragging = False
        self.long_press_event = None
        self.original_x = None

    def on_touch_down(self, touch):
        """Handle touch down"""
        if not self.widget.collide_point(*touch.pos):
            return False

        self.touch_start_pos = touch.pos
        self.touch_start_time = time.time()
        self.is_dragging = False
        self.original_x = self.widget.x

        # Schedule long press check
        self.long_press_event = Clock.schedule_once(
            lambda dt: self._check_long_press(touch),
            self.LONG_PRESS_DURATION
        )

        return True

    def on_touch_move(self, touch):
        """Handle touch move"""
        if self.touch_start_pos is None:
            return False

        # Cancel long press if moved
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None

        # Calculate movement
        dx = touch.pos[0] - self.touch_start_pos[0]
        dy = touch.pos[1] - self.touch_start_pos[1]

        # Check if horizontal swipe
        if abs(dx) > abs(dy) and abs(dx) > dp(10):
            self.is_dragging = True

            # Move widget with touch (for swipe effect)
            if 'on_swipe_move' in self.callbacks:
                self.callbacks['on_swipe_move'](dx)
            else:
                # Default: Move widget
                self.widget.x = self.original_x + dx

        return self.is_dragging

    def on_touch_up(self, touch):
        """Handle touch up"""
        if self.touch_start_pos is None:
            return False

        # Cancel long press
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None

        # Calculate swipe
        dx = touch.pos[0] - self.touch_start_pos[0]
        dy = touch.pos[1] - self.touch_start_pos[1]
        elapsed = time.time() - self.touch_start_time

        result = False

        # Check for swipe gesture
        if (abs(dx) > self.SWIPE_THRESHOLD and
                elapsed < self.SWIPE_TIME_THRESHOLD):

            if dx > 0:
                # Swipe right
                result = self._handle_swipe_right()
            else:
                # Swipe left
                result = self._handle_swipe_left()

        # Check for tap (if not dragging)
        elif not self.is_dragging and elapsed < self.SWIPE_TIME_THRESHOLD:
            result = self._handle_tap(touch)

        # Reset widget position if not handled
        if not result and self.is_dragging:
            self._animate_reset()

        # Reset state
        self.touch_start_pos = None
        self.touch_start_time = None
        self.is_dragging = False
        self.original_x = None

        return result

    def _check_long_press(self, touch):
        """Check for long press"""
        if self.touch_start_pos and not self.is_dragging:
            if 'on_long_press' in self.callbacks:
                self.callbacks['on_long_press'](touch)

    def _handle_tap(self, touch):
        """Handle tap gesture"""
        if 'on_tap' in self.callbacks:
            self.callbacks['on_tap'](touch)
            return True
        return False

    def _handle_swipe_left(self):
        """Handle swipe left (delete/archive)"""
        if 'on_swipe_left' in self.callbacks:
            self.callbacks['on_swipe_left']()
            return True

        # Default: Show delete option
        self._animate_to(-dp(80))
        return True

    def _handle_swipe_right(self):
        """Handle swipe right (complete/mark)"""
        if 'on_swipe_right' in self.callbacks:
            self.callbacks['on_swipe_right']()
            return True

        # Default: Show complete option
        self._animate_to(dp(80))
        return True

    def _animate_to(self, target_x):
        """Animate widget to position"""
        anim = Animation(x=self.original_x + target_x, duration=0.2, t='out_cubic')
        anim.start(self.widget)

    def _animate_reset(self):
        """Animate widget back to original position"""
        anim = Animation(x=self.original_x, duration=0.2, t='out_cubic')
        anim.start(self.widget)


class SwipeToDeleteWidget(Widget):
    """Widget with swipe-to-delete functionality"""

    def __init__(self, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.on_delete = on_delete

        self.gesture_handler = GestureHandler(self, callbacks={
            'on_swipe_left': self._show_delete,
            'on_tap': self._on_tap
        })

        self.delete_revealed = False

    def _show_delete(self):
        """Show delete button"""
        self.delete_revealed = True
        # Animation handled by gesture handler

    def _on_tap(self, touch):
        """Handle tap"""
        if self.delete_revealed:
            # Confirm delete
            if self.on_delete:
                self.on_delete()
            self.gesture_handler._animate_reset()
            self.delete_revealed = False
        else:
            # Normal tap handling
            pass

    def on_touch_down(self, touch):
        if self.gesture_handler.on_touch_down(touch):
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.gesture_handler.on_touch_move(touch):
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.gesture_handler.on_touch_up(touch):
            return True
        return super().on_touch_up(touch)


class PullToRefreshHandler:
    """Handle pull-to-refresh gesture"""

    PULL_THRESHOLD = dp(80)  # Minimum pull distance to trigger refresh

    def __init__(self, scroll_view, on_refresh=None):
        self.scroll_view = scroll_view
        self.on_refresh = on_refresh

        self.touch_start_y = None
        self.is_pulling = False
        self.refreshing = False

        # Bind to scroll view
        scroll_view.bind(on_touch_down=self._on_touch_down)
        scroll_view.bind(on_touch_move=self._on_touch_move)
        scroll_view.bind(on_touch_up=self._on_touch_up)

    def _on_touch_down(self, instance, touch):
        """Track touch start"""
        if self.scroll_view.collide_point(*touch.pos):
            # Only if at top of scroll
            if self.scroll_view.scroll_y >= 0.99:
                self.touch_start_y = touch.pos[1]
                self.is_pulling = False

    def _on_touch_move(self, instance, touch):
        """Track pull distance"""
        if self.touch_start_y is not None and not self.refreshing:
            dy = touch.pos[1] - self.touch_start_y

            # Check if pulling down
            if dy > dp(20) and self.scroll_view.scroll_y >= 0.99:
                self.is_pulling = True

                # Visual feedback (could show spinner/indicator)
                if dy > self.PULL_THRESHOLD:
                    # Ready to refresh
                    pass

    def _on_touch_up(self, instance, touch):
        """Check if should refresh"""
        if self.is_pulling and self.touch_start_y is not None:
            dy = touch.pos[1] - self.touch_start_y

            # Trigger refresh if pulled enough
            if dy > self.PULL_THRESHOLD and not self.refreshing:
                self._trigger_refresh()

        # Reset
        self.touch_start_y = None
        self.is_pulling = False

    def _trigger_refresh(self):
        """Trigger refresh callback"""
        if self.on_refresh:
            self.refreshing = True
            self.on_refresh()

            # Reset after delay (caller should call finish_refresh)
            Clock.schedule_once(lambda dt: self._finish_refresh(), 2)

    def finish_refresh(self):
        """Called when refresh is complete"""
        self.refreshing = False


class DoubleTapHandler:
    """Handle double-tap gesture"""

    DOUBLE_TAP_TIME = 0.3  # Maximum time between taps

    def __init__(self, widget, on_double_tap=None):
        self.widget = widget
        self.on_double_tap = on_double_tap

        self.last_tap_time = 0
        self.tap_count = 0

    def on_touch_down(self, touch):
        """Track taps"""
        if not self.widget.collide_point(*touch.pos):
            return False

        current_time = time.time()

        # Check if within double-tap time
        if current_time - self.last_tap_time < self.DOUBLE_TAP_TIME:
            self.tap_count += 1

            if self.tap_count >= 2:
                # Double tap detected
                if self.on_double_tap:
                    self.on_double_tap(touch)
                self.tap_count = 0
                return True
        else:
            self.tap_count = 1

        self.last_tap_time = current_time
        return False