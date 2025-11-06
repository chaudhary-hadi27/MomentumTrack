from kivymd.app import MDApp
from utils.constants import Colors
import json
import os


class ThemeManager:
    """Centralized theme management with optimized updates"""

    THEME_FILE = "theme_preferences.json"

    def __init__(self):
        self.app = MDApp.get_running_app()
        self.observers = set()  # Widgets that observe theme changes
        self.current_theme = "Dark"
        self.auto_theme = False
        self.theme_colors = {}

        self.load_preferences()
        self.update_theme_colors()

    def load_preferences(self):
        """Load theme preferences from file"""
        if os.path.exists(self.THEME_FILE):
            try:
                with open(self.THEME_FILE, 'r') as f:
                    prefs = json.load(f)
                    self.current_theme = prefs.get('theme', 'Dark')
                    self.auto_theme = prefs.get('auto_theme', False)
            except Exception as e:
                print(f"Error loading theme preferences: {e}")

    def save_preferences(self):
        """Save theme preferences to file"""
        try:
            prefs = {
                'theme': self.current_theme,
                'auto_theme': self.auto_theme
            }
            with open(self.THEME_FILE, 'w') as f:
                json.dump(prefs, f)
        except Exception as e:
            print(f"Error saving theme preferences: {e}")

    def update_theme_colors(self):
        """Update theme color palette"""
        is_dark = self.current_theme == "Dark"

        self.theme_colors = {
            'bg': Colors.DARK_BG if is_dark else Colors.LIGHT_BG,
            'card': Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD,
            'text': Colors.DARK_TEXT if is_dark else Colors.LIGHT_TEXT,
            'hint': Colors.HINT_TEXT_DARK if is_dark else Colors.HINT_TEXT_LIGHT,
            'primary': Colors.PRIMARY_BLUE,
            'success': Colors.SUCCESS_GREEN,
            'danger': Colors.DANGER_RED,
            'border': (0.3, 0.3, 0.3, 1) if is_dark else (0.9, 0.9, 0.9, 1)
        }

    def register_observer(self, widget):
        """Register widget to receive theme updates"""
        self.observers.add(widget)

    def unregister_observer(self, widget):
        """Unregister widget from theme updates"""
        self.observers.discard(widget)

    def set_theme(self, theme_style):
        """Set theme and notify observers"""
        if theme_style not in ["Light", "Dark"]:
            return

        self.current_theme = theme_style

        # Update KivyMD theme
        if self.app:
            self.app.theme_cls.theme_style = theme_style

        # Update color palette
        self.update_theme_colors()

        # Notify observers efficiently
        self._notify_observers()

        # Save preference
        self.save_preferences()

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        new_theme = "Light" if self.current_theme == "Dark" else "Dark"
        self.set_theme(new_theme)

    def _notify_observers(self):
        """Notify all registered observers of theme change"""
        # Batch update to avoid multiple redraws
        for observer in list(self.observers):  # Use list to avoid modification during iteration
            try:
                if hasattr(observer, 'update_theme_colors'):
                    observer.update_theme_colors()
            except Exception as e:
                print(f"Error notifying observer: {e}")
                # Remove invalid observer
                self.observers.discard(observer)

    def get_color(self, color_name):
        """Get color from theme palette"""
        return self.theme_colors.get(color_name, (0, 0, 0, 1))

    @property
    def is_dark(self):
        """Check if current theme is dark"""
        return self.current_theme == "Dark"

    @property
    def theme_style(self):
        """Get current theme style"""
        return self.current_theme


class ThemeAwareWidget:
    """Mixin for widgets that need theme awareness (optimized)"""

    def __init__(self, theme_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = theme_manager
        self._theme_bound = False

        if self.theme_manager:
            self.bind_theme()

    def bind_theme(self):
        """Bind to theme manager"""
        if not self._theme_bound and self.theme_manager:
            self.theme_manager.register_observer(self)
            self._theme_bound = True
            # Initial theme application
            self.update_theme_colors()

    def unbind_theme(self):
        """Unbind from theme manager"""
        if self._theme_bound and self.theme_manager:
            self.theme_manager.unregister_observer(self)
            self._theme_bound = False

    def update_theme_colors(self):
        """Override this method to handle theme changes"""
        pass


# Global theme manager instance
_theme_manager = None


def get_theme_manager():
    """Get global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager