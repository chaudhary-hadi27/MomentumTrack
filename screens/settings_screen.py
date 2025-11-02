from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineListItem, OneLineAvatarIconListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.metrics import dp


class SettingsScreen(MDScreen):
    def __init__(self, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back_callback
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar
        toolbar = MDTopAppBar(
            title="Settings",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=2
        )
        layout.add_widget(toolbar)

        # Settings list
        scroll = MDScrollView()
        settings_list = MDList()

        # Theme setting
        theme_item = OneLineListItem(
            text="Dark Mode",
            on_release=self.toggle_theme
        )
        settings_list.add_widget(theme_item)

        # Show completed tasks
        completed_item = OneLineListItem(
            text="Show Completed Tasks",
        )
        settings_list.add_widget(completed_item)

        # About
        about_item = OneLineListItem(
            text="About",
            on_release=self.show_about
        )
        settings_list.add_widget(about_item)

        scroll.add_widget(settings_list)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def toggle_theme(self, *args):
        # Toggle between light and dark theme
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            app.theme_cls.theme_style = "Dark"
        else:
            app.theme_cls.theme_style = "Light"

    def show_about(self, *args):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="About Tasks",
            text="Momentum Tasks \nVersion 1.0\n\nBuilt with KivyMD",
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