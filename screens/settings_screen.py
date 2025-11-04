from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock


class SettingsScreen(MDScreen):
    def __init__(self, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back_callback
        self.build_ui()

    def get_toolbar_color(self):
        """Get toolbar color based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return (0.12, 0.12, 0.12, 1)  # Dull dark
        else:
            return (0.96, 0.96, 0.96, 1)  # Dull white/light

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar with dull color
        toolbar = MDTopAppBar(
            title="Settings",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )
        layout.add_widget(toolbar)

        # Settings list
        scroll = MDScrollView()
        settings_list = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None
        )
        settings_list.bind(minimum_height=settings_list.setter('height'))

        # Theme setting with switch
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

        # Create switch without active property first
        self.theme_switch = MDSwitch(
            size_hint=(None, None),
            size=(dp(50), dp(30)),
            pos_hint={"center_y": 0.5}
        )
        theme_container.add_widget(self.theme_switch)

        # Set active state after switch is added and bound
        Clock.schedule_once(lambda dt: self._init_switch(), 0.1)

        settings_list.add_widget(theme_container)

        # Divider
        from kivymd.uix.card import MDSeparator
        settings_list.add_widget(MDSeparator())

        # Show completed tasks (future feature)
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

        # Set completed switch active after initialization
        Clock.schedule_once(lambda dt: setattr(self.completed_switch, 'active', True), 0.1)

        settings_list.add_widget(completed_container)

        # Divider
        settings_list.add_widget(MDSeparator())

        # About section
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

    def _init_switch(self):
        """Initialize switch state after widget is ready"""
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
            text="Momentum Track v1.0\n\nA modern task management app designed to help you stay focused and productive.\n\nBuilt with KivyMD",
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