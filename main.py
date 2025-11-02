from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from screens.main_screen import MainScreen
from screens.task_detail_screen import TaskDetailScreen
from screens.settings_screen import SettingsScreen
from utils.constants import PRIMARY_COLOR


class TasksApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Tasks"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.theme_style = "Light"

    def build(self):
        self.screen_manager = ScreenManager()

        # Main screen
        main_screen = Screen(name='main')
        self.main_screen_widget = MainScreen()
        self.main_screen_widget.open_task_details = self.open_task_details
        main_screen.add_widget(self.main_screen_widget)
        self.screen_manager.add_widget(main_screen)

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

    def open_settings(self):
        if not self.screen_manager.has_screen('settings'):
            settings_screen = Screen(name='settings')
            settings_widget = SettingsScreen(
                on_back_callback=self.close_settings
            )
            settings_screen.add_widget(settings_widget)
            self.screen_manager.add_widget(settings_screen)

        self.screen_manager.current = 'settings'

    def close_settings(self):
        self.screen_manager.current = 'main'


if __name__ == '__main__':
    TasksApp().run()