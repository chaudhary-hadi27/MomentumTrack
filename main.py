"""
MomentumTrack - Main Application (Phase 1 & 2 ENHANCED)
✅ Professional themes
✅ No text overlapping
✅ Smooth animations
✅ Responsive design
✅ Enhanced features
"""

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.toast import toast
from datetime import datetime

# Import screens
from screens.home_screen import EnhancedHomeScreen
from screens.task_screen import EnhancedTaskScreen
from screens.time_tracker_screen import TimeTrackerScreen
from screens.goal_screen import GoalScreen
from screens.live_progress_screen import LiveProgressScreen
from screens.settings_screen import EnhancedSettingsScreen

# Import core managers
from database.db_manager import DatabaseManager
from config.settings import AppSettings
from config.theme import ThemeConfig
from utils.motivational_engine import MotivationalEngine


class ResponsiveConfig:
    """Manages responsive sizing - ENHANCED"""

    @staticmethod
    def init():
        screen_width = Window.width
        screen_height = Window.height

        # Use more sophisticated scaling
        baseline_width = 375  # iPhone SE
        baseline_height = 667

        width_scale = screen_width / baseline_width
        height_scale = screen_height / baseline_height

        # Use geometric mean for better scaling
        scale_factor = (width_scale * height_scale) ** 0.5

        # Spacing system (8px grid)
        ResponsiveConfig.SPACING_4 = dp(4 * scale_factor)
        ResponsiveConfig.SPACING_8 = dp(8 * scale_factor)
        ResponsiveConfig.SPACING_12 = dp(12 * scale_factor)
        ResponsiveConfig.SPACING_16 = dp(16 * scale_factor)
        ResponsiveConfig.SPACING_20 = dp(20 * scale_factor)
        ResponsiveConfig.SPACING_24 = dp(24 * scale_factor)
        ResponsiveConfig.SPACING_32 = dp(32 * scale_factor)
        ResponsiveConfig.SPACING_48 = dp(48 * scale_factor)

        # Card dimensions
        ResponsiveConfig.CARD_PADDING = dp(16 * scale_factor)
        ResponsiveConfig.CARD_RADIUS = dp(12 * scale_factor)

        # Button sizes
        ResponsiveConfig.BUTTON_HEIGHT = dp(48 * scale_factor)
        ResponsiveConfig.BUTTON_HEIGHT_SM = dp(36 * scale_factor)
        ResponsiveConfig.BUTTON_HEIGHT_LG = dp(56 * scale_factor)

        # Icon sizes
        ResponsiveConfig.ICON_SIZE_SM = dp(18 * scale_factor)
        ResponsiveConfig.ICON_SIZE_MD = dp(24 * scale_factor)
        ResponsiveConfig.ICON_SIZE_LG = dp(32 * scale_factor)
        ResponsiveConfig.ICON_SIZE_XL = dp(48 * scale_factor)

        # Layout heights
        ResponsiveConfig.HEADER_HEIGHT = dp(64 * scale_factor)
        ResponsiveConfig.NAV_HEIGHT = dp(64 * scale_factor)

        # Card heights
        ResponsiveConfig.STAT_CARD_HEIGHT = min(dp(120), screen_height * 0.15)
        ResponsiveConfig.WELCOME_CARD_HEIGHT = min(dp(140), screen_height * 0.18)
        ResponsiveConfig.ACTION_CARD_HEIGHT = min(dp(56), screen_height * 0.08)

        # Screen classifications
        ResponsiveConfig.is_small_screen = screen_width < 360
        ResponsiveConfig.is_medium_screen = 360 <= screen_width < 400
        ResponsiveConfig.is_large_screen = screen_width >= 400
        ResponsiveConfig.is_tablet = screen_width >= 600

        # Global values
        ResponsiveConfig.SCREEN_WIDTH = screen_width
        ResponsiveConfig.SCREEN_HEIGHT = screen_height
        ResponsiveConfig.SCALE_FACTOR = scale_factor

    @staticmethod
    def get_font_scale():
        """Get font scaling factor"""
        if ResponsiveConfig.is_small_screen:
            return 0.85
        elif ResponsiveConfig.is_large_screen:
            return 1.1
        return 1.0


class MomentumTrackApp(MDApp):
    """Main application - Phase 1 & 2 ENHANCED"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Core managers
        self.db_manager = DatabaseManager()
        self.settings_manager = AppSettings()
        self.motivational_engine = None

        # Initialize responsive config
        ResponsiveConfig.init()

        # Bind to window resize
        Window.bind(on_resize=self.on_window_resize)

        # Reminder scheduler
        self.reminder_scheduler = None

        # Screen manager
        self.sm = None

    def on_window_resize(self, window, width, height):
        """Handle window resize"""
        ResponsiveConfig.init()

        # Refresh current screen
        if self.sm and self.sm.current_screen:
            Clock.schedule_once(lambda dt: self.refresh_current_screen(), 0.1)

    def refresh_current_screen(self):
        """Refresh current screen after resize"""
        if hasattr(self.sm.current_screen, 'rebuild_ui'):
            self.sm.current_screen.rebuild_ui()

    def build(self):
        """Build the application"""
        print("=" * 60)
        print("🚀 MomentumTrack - Phase 1 & 2 Enhanced")
        print("=" * 60)

        # Initialize database
        print("🔧 Initializing database...")
        try:
            self.db_manager.initialize_database()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return None

        # Load and apply theme
        print("🎨 Loading theme...")
        theme_mode = self.settings_manager.get_theme()
        ThemeConfig.apply_theme(self, theme_mode)
        print(f"✅ Theme loaded: {theme_mode}")

        # Adjust font sizes for small screens
        if ResponsiveConfig.is_small_screen:
            self.theme_cls.font_styles["H5"] = ["Roboto", 20, False, 0.15]
            self.theme_cls.font_styles["H6"] = ["Roboto", 18, False, 0.15]
            self.theme_cls.font_styles["Body1"] = ["Roboto", 15, False, 0.15]

        # Initialize motivational engine
        print("💪 Initializing motivational engine...")
        self.motivational_engine = MotivationalEngine(self.db_manager)
        print("✅ Motivational engine ready!")

        # Create screen manager with fade transition
        print("🖥️ Creating screens...")
        try:
            self.sm = ScreenManager(transition=FadeTransition(duration=0.15))

            # Add screens
            self.sm.add_widget(EnhancedHomeScreen(name='home'))
            self.sm.add_widget(EnhancedTaskScreen(name='tasks'))
            self.sm.add_widget(GoalScreen(name='goals'))
            self.sm.add_widget(TimeTrackerScreen(name='time_tracker'))
            self.sm.add_widget(LiveProgressScreen(name='progress'))
            self.sm.add_widget(EnhancedSettingsScreen(name='settings'))

            print("✅ All screens created!")

            # Log screen info
            print("\n" + "=" * 60)
            print("📱 Device Information:")
            print("=" * 60)
            print(f"Screen Size: {ResponsiveConfig.SCREEN_WIDTH:.0f}x{ResponsiveConfig.SCREEN_HEIGHT:.0f}")
            print(f"Scale Factor: {ResponsiveConfig.SCALE_FACTOR:.2f}")
            print(f"Device Type: {'Tablet' if ResponsiveConfig.is_tablet else 'Phone'}")
            print(f"Screen Category: ", end="")
            if ResponsiveConfig.is_small_screen:
                print("Small (<360px)")
            elif ResponsiveConfig.is_medium_screen:
                print("Medium (360-400px)")
            else:
                print("Large (>400px)")
            print("=" * 60 + "\n")

            return self.sm

        except Exception as e:
            print(f"❌ Screen creation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def on_start(self):
        """Initialize app on start"""
        print("🎬 Starting MomentumTrack...")

        # Show daily motivational message (after delay for UI to load)
        Clock.schedule_once(lambda dt: self.show_daily_motivation(), 1)

        # Start reminder scheduler (check every 60 seconds)
        self.reminder_scheduler = Clock.schedule_interval(
            self.check_and_send_reminders, 60
        )

        print("✅ MomentumTrack is ready!")
        print("=" * 60)

    def on_stop(self):
        """Cleanup when app stops"""
        print("\n👋 Stopping MomentumTrack...")
        if self.reminder_scheduler:
            self.reminder_scheduler.cancel()
        print("✅ Cleanup complete")

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
            print(f"⚠️ Reminder error: {e}")

    def show_daily_motivation(self):
        """Show time-based motivational message"""
        try:
            message = self.motivational_engine.get_time_based_message()
            toast(message, duration=3)
        except Exception as e:
            print(f"⚠️ Motivation message error: {e}")

    def switch_theme(self, theme_mode):
        """Switch between Light and Dark themes with animation"""
        # Apply theme
        ThemeConfig.apply_theme(self, theme_mode)
        self.settings_manager.save_theme(theme_mode)

        # Refresh all screens
        Clock.schedule_once(lambda dt: self.refresh_all_screens(), 0.1)

        toast(f"✓ Theme changed to {theme_mode}")

    def refresh_all_screens(self):
        """Refresh all screens after theme change"""
        for screen in self.sm.screens:
            if hasattr(screen, 'rebuild_ui'):
                screen.rebuild_ui()

    def get_motivational_message(self, mode='auto'):
        """Get motivational message from engine"""
        try:
            return self.motivational_engine.get_message(mode)
        except Exception as e:
            print(f"⚠️ Error getting message: {e}")
            return "Keep going! You're doing great! 💪"

    def get_balance_feedback(self, work, personal, sleep):
        """Get feedback on time balance"""
        try:
            return self.motivational_engine.get_balance_feedback(work, personal, sleep)
        except Exception as e:
            print(f"⚠️ Error getting balance feedback: {e}")
            return "Keep working toward balance! 💪"

    def check_productivity_alert(self):
        """Check if user needs productivity alert"""
        try:
            completion_rate = self.db_manager.get_completion_rate()
            threshold = self.settings_manager.get_all_settings().get('progress_threshold', 60)

            if completion_rate < threshold:
                message = self.motivational_engine.get_message('discipline')
                toast(message, duration=3)
                return True

            return False
        except Exception as e:
            print(f"⚠️ Error checking productivity: {e}")
            return False

    def celebrate_achievement(self):
        """Celebrate user achievement"""
        try:
            message = self.motivational_engine.get_message('celebration')
            toast(message, duration=3)
        except Exception as e:
            print(f"⚠️ Error celebrating: {e}")

    def navigate_to(self, screen_name):
        """Navigate to a screen with animation"""
        if self.sm:
            self.sm.current = screen_name


if __name__ == '__main__':
    MomentumTrackApp().run()