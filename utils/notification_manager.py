from datetime import datetime
import threading
import time


class NotificationManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.running = False
        self.thread = None
        self.last_check_time = None

    def start(self):
        """Start notification checker"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._check_notifications, daemon=True)
            self.thread.start()
            print("🔔 Notification manager started")

    def stop(self):
        """Stop notification checker"""
        self.running = False
        if self.thread and self.thread.is_alive():
            print("🔕 Stopping notification manager...")
            # Give thread time to stop gracefully
            time.sleep(1)

    def _check_notifications(self):
        """Check for tasks that need reminders"""
        while self.running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")

                # Skip if we already checked this minute
                if self.last_check_time == current_time:
                    time.sleep(10)  # Check every 10 seconds but skip duplicate minutes
                    continue

                self.last_check_time = current_time

                # Get tasks with reminders - now includes motivation quote
                tasks = self.db.get_tasks_with_reminders_today()

                for task in tasks:
                    task_id, list_id, title, start_time, end_time, reminder_time, motivation_quote = task

                    # Check if it's time to remind
                    if reminder_time and current_time == reminder_time:
                        # Build notification message with motivation quote
                        message = f"Time to work on: {title}"
                        if motivation_quote:
                            message = f"💪 {motivation_quote}\n\n{message}"

                        self.send_notification(title, message)
                        print(f"⏰ Reminder sent for: {title}")
                        if motivation_quote:
                            print(f"   💪 With quote: {motivation_quote}")

                # Sleep for 10 seconds before next check
                time.sleep(10)

            except Exception as e:
                print(f"Notification error: {e}")
                time.sleep(30)  # Wait longer on error

    def send_notification(self, title, message):
        """Send notification (platform dependent)"""
        try:
            # For Android (using plyer when on mobile)
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Momentum Track",
                timeout=10
            )
        except ImportError:
            # Plyer not available (desktop)
            print(f"📢 NOTIFICATION: {title} - {message}")
        except Exception as e:
            # Other errors
            print(f"Notification send error: {e}")
            print(f"📢 NOTIFICATION: {title} - {message}")