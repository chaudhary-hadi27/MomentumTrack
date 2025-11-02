from datetime import datetime
import threading
import time


class NotificationManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.running = False
        self.thread = None

    def start(self):
        """Start notification checker"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._check_notifications, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop notification checker"""
        self.running = False

    def _check_notifications(self):
        """Check for tasks that need reminders"""
        while self.running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")

                tasks = self.db.get_tasks_with_reminders_today()

                for task in tasks:
                    task_id, list_id, title, start_time, end_time, reminder_time = task

                    # Check if it's time to remind
                    if reminder_time and current_time == reminder_time:
                        self.send_notification(title, f"Time to work on: {title}")

                # Check every minute
                time.sleep(60)
            except Exception as e:
                print(f"Notification error: {e}")
                time.sleep(60)

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
        except:
            # Fallback for desktop - just print
            print(f"NOTIFICATION: {title} - {message}")