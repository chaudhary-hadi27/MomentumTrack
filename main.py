from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from screens.main_screen import MainScreen
from screens.task_detail_screen import TaskDetailScreen
from screens.settings_screen import SettingsScreen
from utils.constants import APP_NAME
from utils.notification_manager import NotificationManager
from database.db_manager import DatabaseManager
from datetime import datetime, time
import platform


class MomentumTrackApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_NAME
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.theme_style = "Dark"

        self.db = DatabaseManager()
        self.notification_manager = NotificationManager(self.db)
        self.last_cleanup_date = None

    def build(self):
        self.screen_manager = ScreenManager()

        # Main screen
        main_screen = Screen(name='main')
        self.main_screen_widget = MainScreen()
        self.main_screen_widget.open_task_details = self.open_task_details
        self.main_screen_widget.open_settings = self.open_settings
        main_screen.add_widget(self.main_screen_widget)
        self.screen_manager.add_widget(main_screen)

        # Start notification manager
        self.notification_manager.start()

        # Schedule daily cleanup check (every hour)
        Clock.schedule_interval(self.check_daily_cleanup, 3600)  # Check every hour
        self.check_daily_cleanup(0)  # Initial check

        return self.screen_manager

    def check_daily_cleanup(self, dt):
        """Check if it's a new day and cleanup completed daily tasks"""
        current_date = datetime.now().date()

        # If it's a new day, cleanup
        if self.last_cleanup_date != current_date:
            # Check if it's past midnight (new day)
            current_time = datetime.now().time()
            midnight = time(0, 0)

            # Only cleanup after midnight of new day
            if self.last_cleanup_date is not None:  # Skip first run
                print(f"🧹 Daily cleanup: Removing completed tasks from daily lists")
                self.db.cleanup_completed_daily_tasks()

                # Refresh main screen if on main screen
                if self.screen_manager.current == 'main':
                    self.main_screen_widget.load_tasks()

            self.last_cleanup_date = current_date

    def open_task_details(self, task_id):
        if self.screen_manager.has_screen('task_detail'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('task_detail'))

        detail_screen = Screen(name='task_detail')
        detail_widget = TaskDetailScreen(
            task_id=task_id,
            on_back_callback=self.close_task_details
        )
        detail_screen.add_widget(detail_widget)
        self.screen_manager.add_widget(detail_screen)
        self.screen_manager.current = 'task_detail'

    def close_task_details(self):
        self.main_screen_widget.load_tasks()
        self.screen_manager.current = 'main'
        if self.screen_manager.has_screen('task_detail'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('task_detail'))

    def open_settings(self):
        if self.screen_manager.has_screen('settings'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('settings'))

        settings_screen = Screen(name='settings')
        settings_widget = SettingsScreen(
            on_back_callback=self.close_settings
        )
        settings_screen.add_widget(settings_widget)
        self.screen_manager.add_widget(settings_screen)
        self.screen_manager.current = 'settings'

    def close_settings(self):
        self.screen_manager.current = 'main'
        if self.screen_manager.has_screen('settings'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('settings'))

    def on_stop(self):
        self.notification_manager.stop()


if __name__ == '__main__':
    MomentumTrackApp().run()