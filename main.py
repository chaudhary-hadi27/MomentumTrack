"""
MomentumTrack - Final Main Application with All Enhanced Features
- Task scheduling with start/end time
- Duration options (today/week/month/year/custom)
- Motivational quotes per task
- Live progress tracking (no dummy data)
- Responsive design
"""

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screens.home_screen import HomeScreen
from screens.task_screen import EnhancedTaskScreen
from screens.time_tracker_screen import TimeTrackerScreen
from screens.goal_screen import GoalScreen
from screens.live_progress_screen import LiveProgressScreen
from screens.settings_screen import SettingsScreen
from database.db_manager import DatabaseManager
from config.settings import AppSettings
from utils.motivational_engine import MotivationalEngine
from kivymd.toast import toast
from datetime import datetime
from kivy.metrics import dp
from kivy.clock import Clock

# RESPONSIVE: For desktop testing, uncomment ONE:
# Window.size = (360, 640)   # Small phone
# Window.size = (375, 667)   # iPhone 8
# Window.size = (414, 896)   # iPhone 11


class ResponsiveConfig:
    """Manages responsive sizing"""

    @staticmethod
    def init():
        screen_width = Window.width
        screen_height = Window.height

        baseline_width = 375
        scale_factor = screen_width / baseline_width

        ResponsiveConfig.SPACING_SMALL = dp(8 * scale_factor)
        ResponsiveConfig.SPACING_MEDIUM = dp(16 * scale_factor)
        ResponsiveConfig.SPACING_LARGE = dp(24 * scale_factor)

        ResponsiveConfig.CARD_PADDING = dp(16 * scale_factor)
        ResponsiveConfig.BUTTON_HEIGHT = dp(56 * scale_factor)
        ResponsiveConfig.ICON_SIZE = dp(24 * scale_factor)
        ResponsiveConfig.HEADER_HEIGHT = dp(70 * scale_factor)

        ResponsiveConfig.SMALL_CARD_HEIGHT = screen_height * 0.15
        ResponsiveConfig.MEDIUM_CARD_HEIGHT = screen_height * 0.18
        ResponsiveConfig.LARGE_CARD_HEIGHT = screen_height * 0.25

        ResponsiveConfig.is_small_screen = screen_width < 360
        ResponsiveConfig.is_large_screen = screen_width > 400

        ResponsiveConfig.SCREEN_WIDTH = screen_width
        ResponsiveConfig.SCREEN_HEIGHT = screen_height
        ResponsiveConfig.SCALE_FACTOR = scale_factor

    @staticmethod
    def get_stat_card_height():
        return min(dp(90), ResponsiveConfig.SCREEN_HEIGHT * 0.12)

    @staticmethod
    def get_action_button_height():
        return min(dp(56), ResponsiveConfig.SCREEN_HEIGHT * 0.08)

    @staticmethod
    def get_welcome_card_height():
        if ResponsiveConfig.is_small_screen:
            return min(dp(100), ResponsiveConfig.SCREEN_HEIGHT * 0.14)
        return min(dp(120), ResponsiveConfig.SCREEN_HEIGHT * 0.16)

    @staticmethod
    def get_font_scale():
        if ResponsiveConfig.is_small_screen:
            return 0.85
        elif ResponsiveConfig.is_large_screen:
            return 1.1
        return 1.0


class MomentumTrackApp(MDApp):
    """Main application with all enhanced features"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.settings_manager = AppSettings()
        self.motivational_engine = None

        # Initialize responsive config
        ResponsiveConfig.init()

        # Bind to window resize
        Window.bind(on_resize=self.on_window_resize)

        # Reminder checking
        self.reminder_scheduler = None

    def on_window_resize(self, window, width, height):
        """Handle window resize"""
        ResponsiveConfig.init()

    def build(self):
        """Build the application"""
        # Set theme
        theme_mode = self.settings_manager.get_theme()
        self.theme_cls.theme_style = theme_mode
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"

        # Adjust theme font sizes for small screens
        if ResponsiveConfig.is_small_screen:
            self.theme_cls.font_styles["H5"] = ["Roboto", 20, False, 0.15]
            self.theme_cls.font_styles["H6"] = ["Roboto", 18, False, 0.15]

        # Initialize motivational engine
        self.motivational_engine = MotivationalEngine(self.db_manager)

        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(EnhancedTaskScreen(name='tasks'))
        sm.add_widget(GoalScreen(name='goals'))
        sm.add_widget(TimeTrackerScreen(name='time_tracker'))
        sm.add_widget(LiveProgressScreen(name='progress'))
        sm.add_widget(SettingsScreen(name='settings'))

        return sm

    def on_start(self):
        """Initialize app on start"""
        self.db_manager.initialize_database()

        # Show daily motivational message
        self.show_daily_motivation()

        # Start reminder scheduler (check every 60 seconds)
        self.reminder_scheduler = Clock.schedule_interval(
            self.check_and_send_reminders, 60
        )

        # Log screen info
        print(f"📱 Screen Size: {ResponsiveConfig.SCREEN_WIDTH}x{ResponsiveConfig.SCREEN_HEIGHT}")
        print(f"📏 Scale Factor: {ResponsiveConfig.SCALE_FACTOR:.2f}")
        print(f"📐 Small Screen: {ResponsiveConfig.is_small_screen}")

    def on_stop(self):
        """Cleanup when app stops"""
        if self.reminder_scheduler:
            self.reminder_scheduler.cancel()

    def check_and_send_reminders(self, dt):
        """Check for pending reminders and send notifications"""
        try:
            pending_reminders = self.db_manager.get_pending_reminders()

            for reminder in pending_reminders:
                reminder_id = reminder[0]
                task_title = reminder[4]
                motivational_quote = reminder[5]

                # Show notification
                message = f"⏰ Task: {task_title}"
                if motivational_quote:
                    message += f"\n💬 {motivational_quote[:50]}..."

                toast(message)

                # Mark as sent
                self.db_manager.mark_reminder_sent(reminder_id)

        except Exception as e:
            print(f"Reminder error: {e}")

    def show_daily_motivation(self):
        """Show time-based motivational message"""
        message = self.motivational_engine.get_time_based_message()
        toast(message)

    def switch_theme(self, theme_mode):
        """Switch between Light and Dark themes"""
        self.theme_cls.theme_style = theme_mode
        self.settings_manager.save_theme(theme_mode)
        toast(f"✓ Theme changed to {theme_mode}")

    def get_motivational_message(self, mode='auto'):
        """Get motivational message from engine"""
        return self.motivational_engine.get_message(mode)

    def get_balance_feedback(self, work, personal, sleep):
        """Get feedback on time balance"""
        return self.motivational_engine.get_balance_feedback(work, personal, sleep)

    def check_productivity_alert(self):
        """Check if user needs productivity alert"""
        completion_rate = self.db_manager.get_completion_rate()
        threshold = self.settings_manager.get_all_settings().get('progress_threshold', 60)

        if completion_rate < threshold:
            message = self.motivational_engine.get_message('discipline')
            toast(message)
            return True

        return False

    def celebrate_achievement(self):
        """Celebrate user achievement"""
        message = self.motivational_engine.get_message('celebration')
        toast(message)


if __name__ == '__main__':
    MomentumTrackApp().run()