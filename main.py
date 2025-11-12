from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from screens.main_screen import MainScreen
from screens.task_detail_screen import TaskDetailScreen
from screens.settings_screen import SettingsScreen
from utils.constants import APP_NAME
from utils.notification_manager import NotificationManager
from utils.backup_manager import BackupManager
from database.db_manager import DatabaseManager
from services.task_service import TaskService, ListService
from utils.theme_manager import get_theme_manager
from utils.event_system import event_bus, TaskEvents
from datetime import datetime, time
import platform


class MomentumTrackApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_NAME
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.theme_style = "Dark"

        # Core managers
        self.db = DatabaseManager()

        # SERVICE LAYER (NEW!)
        self.task_service = TaskService(self.db)
        self.list_service = ListService(self.db)

        # Utilities
        self.notification_manager = NotificationManager(self.db)
        self.backup_manager = BackupManager(self.db)
        self.theme_manager = get_theme_manager()

        # State
        self.last_cleanup_date = None

        # Setup event listeners
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup global event listeners"""
        # Task events
        event_bus.on(TaskEvents.TASK_CREATED, self.on_task_created)
        event_bus.on(TaskEvents.TASK_DELETED, self.on_task_deleted)
        event_bus.on(TaskEvents.TASK_COMPLETED, self.on_task_completed)

        # List events
        event_bus.on(TaskEvents.LIST_CREATED, self.on_list_created)
        event_bus.on(TaskEvents.LIST_DELETED, self.on_list_deleted)

    def on_task_created(self, task_id, list_id):
        """Handle task created event"""
        print(f"📝 Task created: {task_id} in list {list_id}")
        # You can add analytics, notifications, etc. here

    def on_task_deleted(self, task_id, list_id):
        """Handle task deleted event"""
        print(f"🗑️ Task deleted: {task_id} from list {list_id}")

    def on_task_completed(self, task_id, completed):
        """Handle task completion event"""
        print(f"✅ Task {task_id} completed: {completed}")

    def on_list_created(self, list_id, category):
        """Handle list created event"""
        print(f"📋 List created: {list_id} in category {category}")

    def on_list_deleted(self, list_id, category):
        """Handle list deleted event"""
        print(f"🗑️ List deleted: {list_id} from category {category}")

    def build(self):
        self.screen_manager = ScreenManager()

        # Set initial theme from saved preference
        self.theme_cls.theme_style = self.theme_manager.theme_style

        # Run database optimization on first launch
        from database.db_optimizer import DatabaseOptimizer
        optimizer = DatabaseOptimizer()
        optimizer.optimize_all()

        # Create auto backup on startup
        print("📦 Creating automatic backup...")
        backup_file = self.backup_manager.auto_backup()
        if backup_file:
            print(f"✅ Auto backup created: {backup_file}")
        else:
            print("⚠️ Auto backup failed")

        # Main screen (now uses service layer)
        main_screen = Screen(name='main')
        self.main_screen_widget = MainScreen(
            task_service=self.task_service,
            list_service=self.list_service
        )
        self.main_screen_widget.open_task_details = self.open_task_details
        self.main_screen_widget.open_settings = self.open_settings
        main_screen.add_widget(self.main_screen_widget)
        self.screen_manager.add_widget(main_screen)

        # Start notification manager (THREAD-SAFE!)
        self.notification_manager.start()

        # Schedule daily cleanup check (every hour)
        Clock.schedule_interval(self.check_daily_cleanup, 3600)
        self.check_daily_cleanup(0)

        # Schedule weekly backup (every 7 days)
        Clock.schedule_interval(lambda dt: self.backup_manager.auto_backup(), 604800)

        # Print service stats on startup
        Clock.schedule_once(lambda dt: self.print_stats(), 5)

        return self.screen_manager

    def check_daily_cleanup(self, dt):
        """Check if it's a new day and cleanup completed daily tasks"""
        current_date = datetime.now().date()

        if self.last_cleanup_date != current_date:
            current_time = datetime.now().time()
            midnight = time(0, 0)

            if self.last_cleanup_date is not None:
                print(f"🧹 Daily cleanup: Removing completed tasks from daily lists")
                self.db.cleanup_completed_daily_tasks()

                # Clear service cache after cleanup
                self.task_service.clear_cache()

                if self.screen_manager.current == 'main':
                    self.main_screen_widget.load_tasks()

            self.last_cleanup_date = current_date

    def open_task_details(self, task_id):
        if self.screen_manager.has_screen('task_detail'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('task_detail'))

        detail_screen = Screen(name='task_detail')
        detail_widget = TaskDetailScreen(
            task_id=task_id,
            task_service=self.task_service,
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

    def print_stats(self):
        """Print service statistics"""
        print("\n" + "=" * 60)
        print("📊 APPLICATION STATISTICS")
        print("=" * 60)

        # Task service stats
        self.task_service.print_stats()

        # Notification stats
        self.notification_manager.print_stats()

        print("=" * 60 + "\n")

    def on_stop(self):
        """Cleanup on app close"""
        print("\n" + "=" * 60)
        print("👋 Application Shutdown")
        print("=" * 60)

        # Print final stats
        self.print_stats()

        # Create backup on app close
        print("📦 Creating exit backup...")
        self.backup_manager.auto_backup()

        # Stop notification manager (GRACEFUL!)
        self.notification_manager.stop()

        # Clear event listeners
        event_bus.clear()

        print("✅ Cleanup complete")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    MomentumTrackApp().run()