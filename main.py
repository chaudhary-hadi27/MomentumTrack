from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from screens.main_screen import MainScreen
from screens.task_detail_screen import TaskDetailScreen
from utils.constants import APP_NAME
from utils.notification_manager import NotificationManager
from database.db_manager import DatabaseManager
import platform


class MomentumTrackApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_NAME
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "600"

        # Auto detect system theme
        self.set_theme_from_system()

        # Initialize notification manager
        self.db = DatabaseManager()
        self.notification_manager = NotificationManager(self.db)

    def set_theme_from_system(self):
        """Auto detect and set theme based on system"""
        try:
            # Try to detect system theme (works on some platforms)
            import darkdetect
            if darkdetect.isDark():
                self.theme_cls.theme_style = "Dark"
            else:
                self.theme_cls.theme_style = "Light"
        except:
            # Default to Light if can't detect
            # You can change this default to "Dark" if you prefer
            self.theme_cls.theme_style = "Light"

    def build(self):
        self.screen_manager = ScreenManager()

        # Main screen
        main_screen = Screen(name='main')
        self.main_screen_widget = MainScreen()
        self.main_screen_widget.open_task_details = self.open_task_details
        main_screen.add_widget(self.main_screen_widget)
        self.screen_manager.add_widget(main_screen)

        # Start notification manager
        self.notification_manager.start()

        return self.screen_manager

    def open_task_details(self, task_id):
        # Check if task detail screen already exists
        if self.screen_manager.has_screen('task_detail'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('task_detail'))

        # Create new task detail screen
        detail_screen = Screen(name='task_detail')
        detail_widget = TaskDetailScreen(
            task_id=task_id,
            on_back_callback=self.close_task_details
        )
        detail_screen.add_widget(detail_widget)
        self.screen_manager.add_widget(detail_screen)

        # Navigate to it
        self.screen_manager.current = 'task_detail'

    def close_task_details(self):
        # Refresh main screen
        self.main_screen_widget.load_tasks()

        # Go back to main screen
        self.screen_manager.current = 'main'

        # Remove detail screen
        if self.screen_manager.has_screen('task_detail'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('task_detail'))

    def on_stop(self):
        # Stop notification manager when app closes
        self.notification_manager.stop()


if __name__ == '__main__':
    MomentumTrackApp().run()