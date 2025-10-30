from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screens.home_screen import HomeScreen
from screens.task_screen import TaskScreen
from screens.time_tracker_screen import TimeTrackerScreen
from screens.settings_screen import SettingsScreen
from database.db_manager import DatabaseManager
from config.settings import AppSettings

Window.size = (400, 700)  # Mobile-like window for testing


class MomentumTrackApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.settings_manager = AppSettings()

    def build(self):
        # Set theme based on saved settings
        theme_mode = self.settings_manager.get_theme()
        self.theme_cls.theme_style = theme_mode
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"

        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TaskScreen(name='tasks'))
        sm.add_widget(SettingsScreen(name='settings'))

        return sm

    def switch_theme(self, theme_mode):
        """Switch between Light and Dark themes"""
        self.theme_cls.theme_style = theme_mode
        self.settings_manager.save_theme(theme_mode)

    def on_start(self):
        """Initialize app on start"""
        self.db_manager.initialize_database()


if __name__ == '__main__':
    MomentumTrackApp().run()