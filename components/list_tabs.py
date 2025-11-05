from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivy.metrics import dp
from kivy.graphics import Color, Line
from kivymd.app import MDApp
from utils.constants import Colors


class ListTabs(MDBoxLayout):
    """Clean horizontal tabs like Google Tasks"""

    def __init__(self, lists=None, on_list_select=None, on_add_list=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(4), 0]
        self.spacing = 0

        self.lists = lists or []
        self.on_list_select = on_list_select
        self.on_add_list = on_add_list
        self.current_list_id = None
        self.tab_buttons = {}

        # Add bottom border
        with self.canvas.after:
            self.border_color = Color(0.9, 0.9, 0.9, 1)
            self.border_line = Line(width=1)

        self.bind(pos=self._update_border, size=self._update_border)

        # Scrollable container
        self.scroll = MDScrollView(
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=0,
            size_hint_x=1
        )

        self.tab_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=0,
            padding=[dp(8), 0]
        )
        self.tab_container.bind(minimum_width=self.tab_container.setter('width'))

        self.scroll.add_widget(self.tab_container)
        self.add_widget(self.scroll)

        # Add button - minimal icon style
        self.add_btn = MDIconButton(
            icon="plus",
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            on_release=lambda x: self.on_add_list() if self.on_add_list else None
        )
        self.add_widget(self.add_btn)

        self.update_tabs()

    def _update_border(self, *args):
        """Update bottom border line"""
        self.border_line.points = [
            self.x, self.y,
            self.x + self.width, self.y
        ]
        # Update border color based on theme
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            self.border_color.rgba = (0.3, 0.3, 0.3, 1)
        else:
            self.border_color.rgba = (0.9, 0.9, 0.9, 1)

    def update_tabs(self):
        """Create clean tab buttons"""
        self.tab_container.clear_widgets()
        self.tab_buttons.clear()

        for lst in self.lists:
            # Create tab button container
            tab_wrapper = MDBoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(120), dp(48)),
                spacing=0
            )

            # Tab button
            btn = MDFlatButton(
                text=lst.name,
                size_hint=(None, None),
                size=(dp(120), dp(45)),
                on_release=lambda x, lid=lst.id: self._on_tab_click(lid),
                md_bg_color=(0, 0, 0, 0)  # Transparent background
            )

            # Bottom indicator line (will be drawn in canvas)
            tab_wrapper.btn = btn
            tab_wrapper.list_id = lst.id

            with tab_wrapper.canvas.after:
                tab_wrapper.indicator_color = Color(0, 0, 0, 0)  # Hidden by default
                tab_wrapper.indicator = Line(width=3)

            tab_wrapper.bind(pos=self._update_indicator, size=self._update_indicator)
            tab_wrapper.add_widget(btn)

            self.tab_buttons[lst.id] = tab_wrapper
            self.tab_container.add_widget(tab_wrapper)

        if self.current_list_id and self.current_list_id in self.tab_buttons:
            self.highlight_tab(self.current_list_id)

    def _update_indicator(self, instance, value):
        """Update indicator line position - centered under tab"""
        if hasattr(instance, 'indicator'):
            # Draw line at bottom center of tab (3px above the border)
            y_pos = instance.y + dp(3)
            instance.indicator.points = [
                instance.x + dp(10), y_pos,
                instance.x + instance.width - dp(10), y_pos
            ]

    def highlight_tab(self, list_id):
        """Highlight selected tab with minimal style"""
        self.current_list_id = list_id
        app = MDApp.get_running_app()
        is_dark = app and app.theme_cls.theme_style == "Dark"

        for lid, tab_wrapper in self.tab_buttons.items():
            btn = tab_wrapper.btn

            if lid == list_id:
                # Active tab - Blue text and indicator
                btn.text_color = Colors.PRIMARY_BLUE
                tab_wrapper.indicator_color.rgba = Colors.PRIMARY_BLUE
            else:
                # Inactive tab - Gray text, no indicator
                if is_dark:
                    btn.text_color = (0.7, 0.7, 0.7, 1)
                else:
                    btn.text_color = (0.4, 0.4, 0.4, 1)
                tab_wrapper.indicator_color.rgba = (0, 0, 0, 0)  # Hide indicator

    def _on_tab_click(self, list_id):
        """Handle tab click"""
        self.highlight_tab(list_id)
        if self.on_list_select:
            self.on_list_select(list_id)

    def set_lists(self, lists):
        """Update lists and rebuild tabs"""
        self.lists = lists
        self.update_tabs()

    def select_list(self, list_id):
        """Programmatically select a list"""
        self.highlight_tab(list_id)