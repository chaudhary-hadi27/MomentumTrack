from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock
from utils.constants import Colors


class SettingsScreen(MDScreen):
    def __init__(self, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back_callback
        self.toolbar = None
        self._theme_bound = False
        self.build_ui()

        # Listen for theme changes
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)
            self._theme_bound = True

    def on_pre_leave(self):
        """Unbind theme when leaving screen"""
        if self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.unbind(theme_style=self.on_theme_change)
                self._theme_bound = False

    def on_pre_enter(self):
        """Re-bind theme when entering screen"""
        if not self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.bind(theme_style=self.on_theme_change)
                self._theme_bound = True

    def update_toolbar_colors(self):
        """Update toolbar icon colors based on theme"""
        if not self.toolbar:
            return

        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = Colors.LIGHT_TEXT
        else:
            self.toolbar.specific_text_color = Colors.DARK_TEXT

    def on_theme_change(self, instance, value):
        """Called when theme changes"""
        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()
            # Rebuild toolbar items
            self.toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]

    def get_toolbar_color(self):
        """Get toolbar color based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return Colors.DARK_BG
        return Colors.LIGHT_BG

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Settings",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )
        self.update_toolbar_colors()
        layout.add_widget(self.toolbar)

        # Settings list
        scroll = MDScrollView()
        settings_list = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None
        )
        settings_list.bind(minimum_height=settings_list.setter('height'))

        # Theme setting
        theme_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0]
        )

        from kivymd.uix.label import MDLabel
        theme_label = MDLabel(
            text="Dark Mode",
            font_style="Body1"
        )
        theme_container.add_widget(theme_label)

        self.theme_switch = MDSwitch(
            size_hint=(None, None),
            size=(dp(50), dp(30)),
            pos_hint={"center_y": 0.5}
        )
        theme_container.add_widget(self.theme_switch)

        # Initialize switch after creation
        Clock.schedule_once(lambda dt: self._init_theme_switch(), 0.1)

        settings_list.add_widget(theme_container)

        # Divider
        from kivymd.uix.card import MDSeparator
        settings_list.add_widget(MDSeparator())

        # Show completed tasks
        completed_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0]
        )

        completed_label = MDLabel(
            text="Show Completed Tasks",
            font_style="Body1"
        )
        completed_container.add_widget(completed_label)

        self.completed_switch = MDSwitch(
            size_hint=(None, None),
            size=(dp(50), dp(30)),
            pos_hint={"center_y": 0.5}
        )
        completed_container.add_widget(self.completed_switch)

        # Initialize completed switch
        Clock.schedule_once(lambda dt: setattr(self.completed_switch, 'active', True), 0.1)

        settings_list.add_widget(completed_container)

        # Divider
        settings_list.add_widget(MDSeparator())

        # App info section
        info_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(16), dp(16)]
        )

        info_container.add_widget(MDLabel(
            text="App Information",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))

        info_container.add_widget(MDLabel(
            text="Momentum Track v1.0",
            font_style="Body2",
            size_hint_y=None,
            height=dp(30)
        ))

        info_container.add_widget(MDLabel(
            text="Time-based task management",
            font_style="Caption",
            size_hint_y=None,
            height=dp(25)
        ))

        settings_list.add_widget(info_container)

        # About button
        from kivymd.uix.button import MDFlatButton
        about_btn = MDFlatButton(
            text="About Momentum Track",
            size_hint_y=None,
            height=dp(48),
            on_release=self.show_about
        )
        settings_list.add_widget(about_btn)

        scroll.add_widget(settings_list)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def _init_theme_switch(self):
        """Initialize theme switch state"""
        app = MDApp.get_running_app()
        self.theme_switch.active = app.theme_cls.theme_style == "Dark"
        self.theme_switch.bind(active=self.toggle_theme)

    def toggle_theme(self, instance, value):
        """Toggle between light and dark theme"""
        app = MDApp.get_running_app()
        if value:
            app.theme_cls.theme_style = "Dark"
        else:
            app.theme_cls.theme_style = "Light"

    def show_about(self, *args):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="About Momentum Track",
            text="Momentum Track v1.0\n\n"
                 "A modern task management app designed to help you stay focused and productive.\n\n"
                 "Features:\n"
                 "• Time-based organization (Daily, Weekly, Monthly, Yearly)\n"
                 "• Task scheduling with reminders\n"
                 "• Subtask support\n"
                 "• Dark/Light theme\n\n"
                 "Built with KivyMD",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()