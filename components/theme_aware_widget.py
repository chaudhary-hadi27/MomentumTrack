from kivy.graphics import Color


class ThemeAwareWidget:
    """Mixin for widgets that need theme awareness"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_colors = {}
        self._theme_bound = False

    def bind_theme(self, theme_manager):
        """Bind to theme manager"""
        if not self._theme_bound:
            theme_manager.register_observer(self)
            self._theme_bound = True
            self.on_theme_change(theme_manager.theme_style)

    def unbind_theme(self, theme_manager):
        """Unbind from theme manager"""
        if self._theme_bound:
            theme_manager.unregister_observer(self)
            self._theme_bound = False

    def on_theme_change(self, theme_style):
        """Override this method to handle theme changes"""
        pass

    def update_color_property(self, color_obj, new_color):
        """Helper to update Color graphics instruction"""
        if isinstance(color_obj, Color):
            color_obj.rgba = new_color